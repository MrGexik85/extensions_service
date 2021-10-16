from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.responses import FileResponse, Response

import os

from app.utils.mongodb import get_database

WORKDB = 'core'

async def get_extension(extension_uuid: UUID, db: AsyncIOMotorClient):
    '''Получение архива плагина с мета информацией с помощь HttpResponse, мета данные хранятся в заголовке'''

    # Получение информации о файле
    extension_info = await db[WORKDB]['extensions'].find_one({'extension_uuid': extension_uuid})

    # Если такого файла не существует
    if extension_info == None:
        return Response(status_code=204, 
                        headers=_get_headers_for_file_not_found_response())

    return Response(status_code=200,
                    content=_get_file_bytes(platform=extension_info['platform'], extension_uuid=str(extension_uuid)), 
                    headers=_get_headers_for_success_response(extension_info))


def _get_headers_for_success_response(extension_info: dict) -> dict:
    '''Заголовок ответа с мета-информацией, если файл найден'''
    return {
        'content-type': 'application/x-zip-compressed',
        'file-extension-uuid': str(extension_info['extension_uuid']),
        'file-platform': extension_info['platform'],
        'file-extension_NAME': extension_info['extension_name'],
        'file-creation_datetime': str(extension_info['creation_datetime']),
    }

def _get_headers_for_file_not_found_response() -> dict:
    '''Заголовок ответа, если файл не будет найден'''
    return {
        'message': 'file not found'
    }

def _get_file_bytes(platform: str, extension_uuid:str) -> bytes:
    '''Получение байтов файла'''
    file_path = os.path.dirname(__file__) + '/../source/' + platform + '_extensions/' + extension_uuid + '.zip'

    with open(file_path, 'rb') as buffer:
        file = buffer.read()
        
    return file