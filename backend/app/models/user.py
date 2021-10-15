from typing import List
from .extension import ExtensionInDB
from pydantic import BaseModel
from uuid import UUID

class UserWithExtensionsResponse(BaseModel):
    user_uuid: UUID
    extensions: List[ExtensionInDB]

class UserInDB(BaseModel):
    user_uuid: UUID
    extensions: List[UUID] = []