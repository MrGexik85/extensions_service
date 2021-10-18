from typing import List
from .extension import ExtensionInDB, Extension
from pydantic import BaseModel
from uuid import UUID, uuid4
from app.utils.mongodb import get_database
from config import DATABASE_WORKDB as WORKDB


class User():
    def __init__(self, user_uuid: UUID = uuid4(), extensions: List[UUID] = []) -> None:
        pass

    async def find_by_uuid(user_uuid: UUID):
        db = await get_database()
        data = await db[WORKDB]['users'].find_one({'_id' : user_uuid})
        if data == None:
            return None
        data['user_uuid'] = data['_id']
        del data['_id']
        return data
    
    async def insert_one(user_uuid: UUID, extensions: List[UUID]):
        db = await get_database()
        await db[WORKDB]['users'].insert_one({
            '_id': user_uuid,
            'extensions': extensions
        })

    async def update_extensions_by_uuid(user_uuid: UUID, extensions: list):
        db = await get_database()
        await db[WORKDB]['users'].update_one({'_id' : user_uuid}, {'$set' : {'extensions' : extensions}})


class UserDeleteExtensionResponse(BaseModel):
    success: bool
    message: str
    user_uuid: UUID
    extension: ExtensionInDB

class UserWithExtensionsResponse(BaseModel):
    success: bool
    user_uuid: UUID
    extensions: List[ExtensionInDB]

class UserNewExtensionResponse(BaseModel):
    success: bool
    message: str
    user_uuid: UUID
    extension: ExtensionInDB

class UserInDB(BaseModel):
    user_uuid: UUID
    extensions: List[UUID] = []