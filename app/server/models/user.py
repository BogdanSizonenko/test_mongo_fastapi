from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from .notifications import NotificationSchema

# Модели для User-а
class UserSchema(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    notifications: list = Field(examples=[[]])