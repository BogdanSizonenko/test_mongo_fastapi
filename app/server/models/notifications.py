from pydantic import BaseModel, Field
from enum import Enum


   
# Модели для уведомлений User-a       
class Key(Enum):
    registration = "registration"
    new_message = "new_message"
    new_post = "new_post"
    new_login = "new_login"


class NotificationSchema(BaseModel):
    timestamp: str = Field(examples=['устанавливается автоматически'])
    is_new: bool 
    user_id: str = Field(..., examples=["ID пользователя"])
    key: Key = Field(..., examples=["new_post"])
    target_id: str = Field(examples=["ID документа"])
    data: dict = Field(examples=[
        {
        'some field': 'some values'
        }
                                 ],)

    
class MarkReadNotification(BaseModel):
    notification_id: str = Field(..., examples=["ID уведомления"])
    user_id: str = Field(..., examples=["ID пользователя"])


def ResponseModel(data, message, code=200):
    return {
        "data": [data],
        "code": code,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}