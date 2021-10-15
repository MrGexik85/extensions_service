from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends

from app.utils.mongodb import get_database


async def get_extension(extension_uuid: str, db: AsyncIOMotorClient = Depends(get_database)):
    ''''''
    return {
        "success": True,
        'data': {
            'message': 'get extension zip file',
            'extension_uuid': extension_uuid,    
        }
    }