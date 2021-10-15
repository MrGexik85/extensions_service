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

async def user_extensions(user_uuid: str, 
                          db:AsyncIOMotorClient):
    ''''''
    return {
        "success": True,
        'data': {
            'message': 'get user extensions',
            'user_uuid': user_uuid   
        }
    }

async def delete_extension(user_uuid: str, 
                           extension_uuid:str, 
                           db:AsyncIOMotorClient):
    '''Delete extension and return Extension object in response'''
    return {
        "success": True,
        'data': {
            'message': 'delete user extension',
            'user_uuid': user_uuid,
            'extension_uuid': extension_uuid
        }
    }

async def add_extension(user_uuid: UUID, 
                        platform_name: str, 
                        file: UploadFile,
                        db:AsyncIOMotorClient):
    ''''''
    extension_document = {
        'extension_uuid' : uuid4(),
        'platform': platform_name,
        'extension_name' : file.filename,
        'creation_datetime' : datetime.now()
    }

    # проверка MIME файла (.zip)
    if file.content_type not in ZIP_MIME:
        return {'success': False, 'message': 'Uncorrect MIME type of file'}

    if (platform_name == "Chrome"):
        _save_extension_file(platform_directory='Chrome_extensions', 
                            filename=str(extension_document['extension_uuid']) + '.zip', 
                            file=file)
    elif (platform_name == "Mozilla"):
        _save_extension_file(platform_directory='Mozilla_extensions', 
                            filename=str(extension_document['extension_uuid']) + '.zip', 
                            file=file)
    else:
        return {'success' : False, 'message' : 'Unknown platform name'}
    
    result = db[WORKDB]['extensions'].insert_one(extension_document)

    user = await db[WORKDB]['users'].find_one({'user_uuid' : user_uuid})
    if user == None:
        return _new_user_with_extension(user_uuid, extension_document, db)
    else:
        return _add_extension_to_exist_user(user, extension_document, db)

    # arr = user_ext['extensions']
    # arr.append(extension_document['_id'])
    # db[WORKDB]['users'].replace_one({'_id' : user_uuid}, {'extensions' : arr})

    result = db[WORKDB]['extensions'].insert_one(extension_document)
    
    if result:
        return {'success': True}
    # if file.content_type in ZIP_MIME:
    #     return {
    #         'success': True,
    #         'data': {
    #             'message': 'create new extension for user',
    #             'user_uuid': user_uuid,
    #             'platform': platform_name,
    #             'filename': file.filename,
    #             'MIME': file.content_type,
    #         }
    #     }
    # else:
    #     return {
    #         'success': False,
    #         'data': {
    #             'message': 'File is not zip archive',
    #         }
    #     }


def _save_extension_file(platform_directory:str, filename:str, file: UploadFile):
    '''Сохраняет file в директории platform_directory'''
    cur_path = os.path.dirname(__file__)
    new_path = cur_path + '/../source/' + platform_directory + '/' + filename
    with open(new_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

def _add_extension_to_exist_user(user, extension, db:AsyncIOMotorClient):
    '''Добавляет extension_uuid в user.extensions'''
    
    user_extensions = user['extensions']
    print(user_extensions)
    user_extensions.append(extension['extension_uuid'])
    db[WORKDB]['users'].update_one({'user_uuid' : user['user_uuid']}, {'$set' : {'extensions' : user_extensions}})
    print(user_extensions)
    return {'success': True, 'message': 'Add extension to exist user'}

def _new_user_with_extension(user_uuid: UUID, extension_document, db:AsyncIOMotorClient):
    ''''''
    new_user_document = {
            'user_uuid' : user_uuid,
            'extensions' : [extension_document['extension_uuid']],
    }
    result = db[WORKDB]['users'].insert_one(new_user_document)
    return {'success': True, 'message': 'Create new user with extension info'}