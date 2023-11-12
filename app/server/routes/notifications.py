from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

from ..database import (
    add_notification,
    read_notification,
    send_email,
    get_list_notifications,
)
from ..models.notifications import (
    ResponseModel,
)
from ..models.notifications import(
    NotificationSchema,
    MarkReadNotification,
)



router = APIRouter()


#Точка добавления уведомления в документ пользователя
@router.post("/", response_description="Добавление уведомления в документ пользователя")
async def add_notification_data(notification: NotificationSchema = Body(...)):
    notification = jsonable_encoder(notification)
    id = ObjectId()
    notification['timestamp'] = str(id.generation_time)
    if notification["key"] == 'registration':
        await send_email(notification)
        return ResponseModel((notification['key'], notification['user_id']), "Created", code=201)
    elif notification["key"] == "new_login":
        await send_email(notification)
    await add_notification(notification)
    return ResponseModel((notification['key'], notification['user_id']), "Created", code=201)


#Точка отметки прочтения уведомления
@router.post("/read", response_description="Отметка о прочтении уведомления")
async def mark_read_notification(notification: MarkReadNotification = Body(...)):
    notification = jsonable_encoder(notification)
    mark_read = await read_notification(notification)
    return ResponseModel({'notification_id': str(mark_read['_id']), 
                          'user_id': mark_read['user_id'], 
                          "is_new": mark_read['is_new']}, 
                         'Ok', 200)


# Точка получения списка уведомлений(листинг) 
@router.get("/list", response_description="Листинг уведомлений")
async def list_notifications(user_id: str, skip: int = 0, limit: int = 0):
    list_notifications = await get_list_notifications(user_id, skip, limit)
    return {
        'list': list_notifications,
        'code': 200,
        'message': "OK",
    }
    
    
