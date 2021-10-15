from fastapi import APIRouter, Depends, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorClient

from app.utils.mongodb import get_database
from app.models.user import UserWithExtensionsResponse
from app.services.user_service import * # Сделать нужные импорты
import app.services.user_service as user_service
import app.services.extension_service as extension_service
from app.models.users import UserInResponse


router = APIRouter()

@router.get('/extension/{extension_uuid}')
async def get_extension(extension_uuid: str):
    '''Найти расширение по uuid и выдать zip архив'''
    # Какая нибудь валидация запроса 
    response = await extension_service.get_extension(extension_uuid)
    return response

@router.get('/user/{user_uuid}/extensions') 
async def get_user_extensions(user_uuid: str):
    '''Выдать JSON все записи модели Extension для переданного пользователя'''
    # Какая нибудь валидация запроса 
    response = await user_service.user_extensions(user_uuid)
    return response

@router.delete('/user/{user_uuid}/delete_extension/{extension_uuid}')
async def del_user_extension(user_uuid: str, extension_uuid: str):
    '''Удалить расширение для переданнного пользователя'''
    # Валидация
    response = await user_service.delete_extension(user_uuid, extension_uuid)
    return response

@router.post('/user/{user_uuid}/new_extension')
async def new_user_extension(user_uuid: str, 
                            platform_name: str, 
                            file: UploadFile = File(...)):
    '''Получить файл в формате .zip, сохранить его и добавить информацию в бд'''
    #Валидация 
    response = await user_service.add_extension(user_uuid, platform_name, file)
    return response

# @router.get("/", response_model=UserInResponse, tags=["users"])
# async def get_all_users(db: AsyncIOMotorClient = Depends(get_database)) -> UserInResponse:
#     """
#     Get a list of users in the database

#     Each item will have a set of params
#     """
#     users = []
#     rows = db["core"]["users"].find()
#     async for row in rows:
#         users.append(row)
#     return UserInResponse(users=users)



# @router.get("/{item_id}")
# async def read_item(item_id: str):
#     return {"name": "Fake Specific Item", "item_id": item_id}
