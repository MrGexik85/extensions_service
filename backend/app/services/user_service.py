from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends, UploadFile

from app.utils.mongodb import get_database

async def user_extensions(user_uuid: str, db:AsyncIOMotorClient = Depends(get_database)):
    ''''''
    return {
        "success": True,
        'data': {
            'message': 'get user extensions',
            'user_uuid': user_uuid    
        }
    }

async def delete_extension(user_uuid: str, extension_uuid:str, db:AsyncIOMotorClient = Depends(get_database)):
    ''''''
    return {
        "success": True,
        'data': {
            'message': 'delete user extension',
            'user_uuid': user_uuid,
            'extension_uuid': extension_uuid
        }
    }

async def add_extension(user_uuid: str, 
                        platform_name: str, 
                        file: UploadFile):
    ''''''
    return {
        'success': True,
        'data': {
            'message': 'create new extension for user',
            'user_uuid': user_uuid,
            'platform': platform_name,
            'filename': file.filename,
        }
    }