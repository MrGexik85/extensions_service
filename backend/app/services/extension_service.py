from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.responses import FileResponse, Response

import os

from app.utils.mongodb import get_database

WORKDB = 'core'

async def get_extension(extension_uuid: UUID, db: AsyncIOMotorClient):
    '''Получение архива плагина с мета информацией с помощь HttpResponse, мета данные хранятся в заголовке'''

    extension_info = await db[WORKDB]['extensions'].find_one({'extension_uuid': extension_uuid})
    if extension_info == None:
        print("Давай по новой")
        return Response(status_code=204)
    
    file_path = os.path.dirname(__file__) + '/../source/' + extension_info['platform'] + '_extensions/' + str(extension_uuid) + '.zip'
    with open(file_path, 'rb') as buffer:
        file = buffer.read()
    
    headers = {
        'content-type': 'application/x-zip-compressed',
        'file-extension-uuid': str(extension_info['extension_uuid']),
        'file-platform': extension_info['platform'],
        'file-extension_NAME': extension_info['extension_name'],
        'file-creation_datetime': str(extension_info['creation_datetime']),
    }
    return Response(file, headers=headers)
    # return {
    #     'success': True,
    #     'extension_info': {
    #         'extension_uuid': extension_info['extension_uuid'],
    #         'platform': extension_info['platform'],
    #         'extension_name': extension_info['extension_name'],
    #         'creation_datetime': extension_info['creation_datetime'],
    #     },
    #     #'extension_file': file,
    # }