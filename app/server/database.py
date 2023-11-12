import motor.motor_asyncio
from bson.objectid import ObjectId
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pymongo import DeleteOne
import os
from dotenv import load_dotenv


load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD'),
    MAIL_FROM = os.getenv('MAIL_FROM'),
    MAIL_PORT = os.getenv('MAIL_PORT'),
    MAIL_SERVER = os.getenv('MAIL_SERVER'),
    MAIL_STARTTLS = os.getenv('MAIL_STARTTLS'),
    MAIL_SSL_TLS = os.getenv('MAIL_SSL_TLS'),
)

MONGO_DETAILS = os.getenv('MONGO_DETAILS')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

# База с user-ами
database = client.users

user_collection = database.get_collection("users_collection")
notifications_collection = database.get_collection('notifications_collection')   


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user['email'],
        "notifications": user['notifications'],
    }


# Получить всех users
async def retrieve_users():
    users = []
    async for user in user_collection.find():
        users.append(user_helper(user))
        notifications_list = await get_list(users[-1]['id'])
        users[-1]['notifications'] = notifications_list
    return users


# Добавить нового user
async def add_user(user_data: dict) -> dict:
    user = await user_collection.insert_one(user_data)
    new_user = await user_collection.find_one({"_id": user.inserted_id})
    return user_helper(new_user)


# Получить user с соответствующим ID
async def retrieve_user(id: str) -> dict:
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        return user_helper(user)


def notification_helper(notification) -> dict:
    return {
        'id': str(notification['_id']),
        'timestamp': notification['timestamp'],
        'is_new': notification['is_new'],
        'user_id': notification['user_id'],
        'key': notification['key'],
        'target_id': notification['target_id'],
        'data': notification['data']
    }
    
    
def list_notifications_helper(user_id, limit, skip, notification_list, new, elements) -> dict:
    return {
        "success": "true",
        "data": {
            "elements": elements,
            "new": new,
            "request": {
                'user_id': user_id,
                'skip': skip,
                'limit': limit,
                }
            },
        "list": notification_list,
    }    


# Добавление уведомления
async def add_notification(notifications_data: dict) -> dict:
    await notifications_collection.insert_one(notifications_data)
    elements = await count_notificate(notifications_data['user_id'])
    if elements > 20:
        requests = [DeleteOne({'user_id': notifications_data['user_id']}) for i in range(elements - 20)]
        await notifications_collection.bulk_write(requests)
    return notification_helper(notifications_data)


# Делает отметку о прочтении, изменяя значение is_new на False
async def read_notification(notifications_data: dict) -> dict:
    await notifications_collection.update_one(
                                    {"_id": ObjectId(notifications_data['notification_id']), 
                                     "user_id": notifications_data['user_id']},
                                    {"$set" : {"is_new" : False}}
                                     )
    mark_is_new = await notifications_collection.find_one(
                                    {"_id": ObjectId(notifications_data['notification_id']), 
                                    "user_id": notifications_data['user_id']})
    return mark_is_new


# Листинг уведомлений    
async def get_list_notifications(user_id, skip, limit):
    elements = await count_notificate(user_id)
    new = await notifications_collection.count_documents({'user_id': user_id, 'is_new': True})
    notification_list = await get_list(user_id, skip, limit)
    return list_notifications_helper(user_id, limit, skip, notification_list, new, elements)


# Создает список уведомлений пользователя
async def get_list(user_id, skip=0, limit=0):
    notification_list = []
    cursor = notifications_collection.find({"user_id": user_id}).limit(limit).skip(skip)
    async for doc in cursor:
        notification_list.append(notification_helper(doc))
    return notification_list


# Считает количество уведомлений у пользователя
async def count_notificate(user_id):
    elements = await notifications_collection.count_documents({"user_id": user_id})
    return elements


# Отправка email
async def send_email(notifications_data: dict) -> dict:
    email = await user_collection.find_one({"_id": ObjectId(notifications_data["user_id"])},  
                                           {"email": 1})
    
    email = email["email"]
    body = 'Уведомление'
    message = MessageSchema(
        subject="Notification",
        recipients=[email],
        body=body,
        subtype=MessageType.html
    )
    fast_mail = FastMail(conf)
    await fast_mail.send_message(message)
    return "Email отправлен"