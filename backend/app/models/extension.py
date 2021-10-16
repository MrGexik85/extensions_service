from pydantic import BaseModel
from datetime import datetime
from fastapi import File, UploadFile
from uuid import UUID

from app.utils.mongodb import get_database

WORKDB = 'core'

class Extension():
    def __init__(self, extensions: dict) -> None:
        pass
    
    async def find_by_uuid(extension_uuid: UUID):
        db = await get_database()
        data = await db[WORKDB]['extensions'].find_one({'_id': extension_uuid})
        if data == None:
            return None
        data['extension_uuid'] = data['_id']
        del data['_id']
        return data
    
    async def insert_one(extension: dict):
        db = await get_database()
        await db[WORKDB]['extensions'].insert_one({
            '_id': extension['extension_uuid'],
            'platform': extension['platform'],
            'extension_name': extension['extension_name'],
            'creation_datetime': extension['creation_datetime']
        })

    async def delete_extension_by_uuid(extension_uuid: UUID):
        db = await get_database()
        await db[WORKDB]['extensions'].delete_one({'_id' : extension_uuid})


class ExtensionInDB(BaseModel):
    extension_uuid: UUID
    extension_name: str
    platform: str
    creation_datetime: datetime

