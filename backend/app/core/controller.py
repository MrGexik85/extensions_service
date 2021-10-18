from uuid import UUID
from app.models.user import UserWithExtensionsResponse, UserNewExtensionResponse, UserDeleteExtensionResponse
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

import app.services.user_service as user_service
import app.services.extension_service as extension_service




router = APIRouter()

@router.get('/extension/{extension_uuid}')
async def get_extension(extension_uuid: str):
    '''Найти расширение по uuid и выдать zip архив'''
    try:
        extension_uuid = UUID(extension_uuid)
    except ValueError as err:
        return _get_error_response('Badly uuid format')
    # Какая нибудь валидация запроса 
    response = await extension_service.get_extension(extension_uuid)
    return response

@router.get('/user/{user_uuid}/extensions', response_model=UserWithExtensionsResponse) 
async def get_user_extensions(user_uuid: str):
    '''Выдать JSON все записи модели Extension для переданного пользователя'''
    try:
        user_uuid = UUID(user_uuid)
    except ValueError as err:
        return _get_error_response('Badly uuid format')
    # Какая нибудь валидация запроса 
    response = await user_service.user_extensions(user_uuid)
    return response

@router.delete('/user/{user_uuid}/delete_extension/{extension_uuid}', response_model=UserDeleteExtensionResponse)
async def del_user_extension(user_uuid: str, extension_uuid: str):
    '''Удалить расширение для переданнного пользователя'''
    try:
        user_uuid = UUID(user_uuid)
        extension_uuid = UUID(extension_uuid)
    except ValueError as err:
        return _get_error_response('Badly uuid format')
    # Валидация
    response = await user_service.delete_extension(user_uuid, extension_uuid)
    return response

@router.post('/user/{user_uuid}/new_extension', response_model=UserNewExtensionResponse)
async def new_user_extension(user_uuid: str, 
                            platform_name: str, 
                            file: UploadFile = File(...)):
    '''Получить файл в формате .zip, сохранить его и добавить информацию в бд'''
    try:
        user_uuid = UUID(user_uuid)
    except ValueError as err:
        return _get_error_response('Badly uuid format')
    #Валидация 
    response = await user_service.add_extension(user_uuid, platform_name, file)
    return response


def _get_error_response(message: str) -> JSONResponse:
    '''Объект для ответа при ошибке с сообщением message'''
    return JSONResponse({
        'success': False, 
        'message': message
    })
