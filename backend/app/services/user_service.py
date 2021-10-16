from datetime import datetime
from uuid import UUID, uuid4
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import UploadFile
import os
import shutil


from app.utils.mongodb import get_database

from app.models.extension import ExtensionInDB


WORKDB = 'core'
ZIP_MIME = ['application/zip', 'application/octet-stream', 'application/x-zip-compressed', 'multipart/x-zip']
PLATFORMS = ['Chrome', 'Mozilla']

async def user_extensions(user_uuid: UUID, 
                          db:AsyncIOMotorClient):
    '''Возвращает все extensions для выбранного пользователя'''

    user = await db[WORKDB]['users'].find_one({'user_uuid' : user_uuid}) # Попытка получить пользователя с user_uuid
    if user == None:
        return _get_user_extensions_response(user_uuid=str(user_uuid), extensions=[])
    
    extensions = user['extensions']
    response_extensions = await _get_user_extensions_advanced(extensions, db)

    return _get_user_extensions_response(user_uuid=str(user_uuid), extensions=response_extensions)

def _get_user_extensions_response(user_uuid: str, extensions: list) -> dict:
    '''Получение объекта ответа с плагинами пользователя'''
    return {
        'success': True,
        'user_uuid': user_uuid,
        'extensions' : extensions
    }

async def _get_user_extensions_advanced(extensions, db) -> list:
    '''Замена массива extensions с UUID на массив extensions с объектами Extension'''
    response_extensions = []
    for extension_uuid in extensions:
        extension = await db[WORKDB]['extensions'].find_one({'extension_uuid' : extension_uuid})
        tmp = {
            'extension_uuid' : str(extension['extension_uuid']),
            'platform' : extension['platform'],
            'extension_name' : extension['extension_name'],
            'creation_datetime' : extension['creation_datetime']
        }
        response_extensions.append(tmp)
    return response_extensions

async def delete_extension(user_uuid: UUID, 
                           extension_uuid:UUID, 
                           db:AsyncIOMotorClient):
    '''Удаление extension'''
    user = await db[WORKDB]['users'].find_one({'user_uuid' : user_uuid}) # Попытка получить пользователя с user_uuid

    if user == None:
        return _get_error_response('Not found user with this user_uuid')

    user_extensions = user['extensions']
    if extension_uuid not in user_extensions:
        return _get_error_response('Not found extension_uuid for this user_uuid')
    
    # Сделать удаление из [extensions] объекта user
    try:
        user_extensions.remove(extension_uuid)
    except ValueError as err:
        return _get_error_response('Something went wrong when deleting the file')

    db[WORKDB]['users'].update_one({'user_uuid' : user_uuid}, {'$set' : {'extensions' : user_extensions}})

    extension = await db[WORKDB]['extensions'].find_one({'extension_uuid' : extension_uuid})
    if extension == None:
        return _get_error_response('Not found extension in extensions collection')

    platform = extension['platform']
    db[WORKDB]['extensions'].delete_one({'extension_uuid' : extension_uuid})

    _remove_extension_file(platform=platform, extension_uuid=str(extension_uuid))

    return _get_success_delete_response(extension)

async def add_extension(user_uuid: UUID, 
                        platform_name: str, 
                        file: UploadFile,
                        db:AsyncIOMotorClient):
    '''Создание записи extension и сохранение файла'''

    # Создание сущности Extension
    extension_document = {
        'extension_uuid' : uuid4(),
        'platform': platform_name,
        'extension_name' : file.filename,
        'creation_datetime' : datetime.now()
    }

    # проверка MIME файла (.zip)
    if file.content_type not in ZIP_MIME:
        return {'success': False, 'message': 'Uncorrect MIME-type of file'}

    # Проверка platform_name и сохранение в нужной директории
    if platform_name in PLATFORMS:
        _save_extension_file(platform_directory=platform_name + '_extensions', 
                            filename=str(extension_document['extension_uuid']) + '.zip', 
                            file=file)
    else:
        return {'success' : False, 'message' : 'Unknown platform name'}
    
    db[WORKDB]['extensions'].insert_one(extension_document) # Добавление extension записи
    user = await db[WORKDB]['users'].find_one({'user_uuid' : user_uuid}) # Попытка получить пользователя с user_uuid

    # Создание нового пользователя или добавление к существующему
    if user == None:
        return _new_user_with_extension(user_uuid, extension_document, db)
    else:
        return _add_extension_to_exist_user(user, extension_document, db)

def _get_success_delete_response(extension: dict) -> dict:
    '''Ответ при успешном удалении плагина пользователя'''
    return {
        "success": True,
        'message': 'The extension was been removed',
        'extension' : {
            'extension_uuid' : extension['extension_uuid'],
            'platform' : extension['platform'],
            'extension_name' : extension['extension_name'],
            'creation_datetime' : extension['creation_datetime'],
        }
    }

def _get_error_response(message: str) -> dict:
    '''Объект для ответа при ошибке с сообщением message'''
    return {
        'success': False,
        'message': message
    }

def _remove_extension_file(platform: str, extension_uuid: str):
    file_path = os.path.dirname(__file__) + '/../source/' + platform + '_extensions/' + extension_uuid + '.zip'
    os.remove(file_path)

def _save_extension_file(platform_directory:str, filename:str, file: UploadFile):
    '''Сохраняет file в директории platform_directory'''
    path = os.path.dirname(__file__) + '/../source/' + platform_directory + '/' + filename # путь до директории app/source/<platform>_extensions

    with open(path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

def _add_extension_to_exist_user(user, extension, db:AsyncIOMotorClient):
    '''Добавляет extension_uuid в user.extensions'''
    user_extensions = user['extensions']
    if user_extensions == None:
        user_extensions = []
    user_extensions.append(extension['extension_uuid']) # Взять имеющийся массив extensions и добавить один новый элемент

    db[WORKDB]['users'].update_one({'user_uuid' : user['user_uuid']}, {'$set' : {'extensions' : user_extensions}})

    return {'success': True, 'message': 'Add extension to exist user', 
    'user_uuid' : user['user_uuid'],
    'extension' : {
        'extension_uuid' : extension['extension_uuid'],
        'platform' : extension['platform'],
        'extension_name' : extension['extension_name'],
        'creation_datetime' : extension['creation_datetime'],
    }}

def _new_user_with_extension(user_uuid: UUID, extension, db:AsyncIOMotorClient):
    '''Создает в коллекции users новую запись'''
    new_user_document = {
            'user_uuid' : user_uuid,
            'extensions' : [extension['extension_uuid']],
    }

    db[WORKDB]['users'].insert_one(new_user_document)

    return {'success': True, 'message': 'Create new user with extension', 
    'user_uuid' : new_user_document['user_uuid'],
    'extension': {
        'extension_uuid' : extension['extension_uuid'],
        'platform' : extension['platform'],
        'extension_name' : extension['extension_name'],
        'creation_datetime' : extension['creation_datetime'],
    }}