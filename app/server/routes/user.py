from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from ..database import (
    add_user,
    retrieve_user,
    retrieve_users,
)
from ..models.notifications import(
    ErrorResponseModel,
    ResponseModel,
)
from ..models.user import (
    UserSchema,
)



router = APIRouter()


@router.post("/", response_description="Добавление user в базу данных")
async def add_user_data(user: UserSchema = Body(...)):
    user = jsonable_encoder(user)
    new_user = await add_user(user)
    return ResponseModel(new_user, "User успешно добавлен!")


@router.get("/", response_description="Получить список user")
async def get_users():
    users = await retrieve_users()
    if users:
        return ResponseModel(users, "User список успешно получен")
    return ResponseModel(users, "Список пуст")


@router.get("/{id}", response_description="Получить информацию по одному user")
async def get_user_data(id):
    user = await retrieve_user(id)
    if user:
        return ResponseModel(user, "User успешно получен")
    return ErrorResponseModel("Ошибка.", 404, "User отсутствует.")