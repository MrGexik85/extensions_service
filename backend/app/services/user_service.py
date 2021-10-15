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
        return {'success' : True, 'user': {
            'user_uuid' : user_uuid,
            'extensions' : []
        }}
    
    extensions = user['extensions']
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

    return {
        'success' : True,
        'user_uuid' : str(user_uuid),
        'extensions' : response_extensions
    }

async def delete_extension(user_uuid: UUID, 
                           extension_uuid:UUID, 
                           db:AsyncIOMotorClient):
    '''Удаление extension'''
    user = await db[WORKDB]['users'].find_one({'user_uuid' : user_uuid}) # Попытка получить пользователя с user_uuid
    if user == None:
        return {
            'success': False,
            'message': 'There is no user with this user_uuid'
        }

    user_extensions = user['extensions']
    if extension_uuid not in user_extensions:
        return {
            'success': False,
            'message': 'There is no extension_uuid for this user_uuid'
        }
    
    # Сделать удаление
    try:
        user_extensions.remove(extension_uuid)
    except ValueError as err:
        return {
            'success' : False,
            'message': 'Something went wrong!'
        }
    db[WORKDB]['users'].update_one({'user_uuid' : user_uuid}, {'$set' : {'extensions' : user_extensions}})

    extension = await db[WORKDB]['extensions'].find_one({'extension_uuid' : extension_uuid})
    # Может тоже быть none
    platform = extension['platform']
    db[WORKDB]['extensions'].delete_one({'extension_uuid' : extension_uuid})

    file_path = os.path.dirname(__file__) + '/../source/' + platform + '_extensions/' + str(extension_uuid) + '.zip'
    os.remove(file_path)

    return {
        "success": True,
        'message': 'delete user extension',
        'extension' : {
            'extension_uuid' : extension['extension_uuid'],
            'platform' : extension['platform'],
            'extension_name' : extension['extension_name'],
            'creation_datetime' : extension['creation_datetime'],
        }
    }

async def add_extension(user_uuid: UUID, 
                        platform_name: str, 
                        file: UploadFile,
                        db:AsyncIOMotorClient):
    '''Создание записи extension и сохранение файла'''

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