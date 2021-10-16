from typing import List
from .extension import ExtensionInDB
from pydantic import BaseModel
from uuid import UUID

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