from pydantic import BaseModel
from datetime import datetime
from fastapi import File, UploadFile
from uuid import UUID




class ExtensionInDB(BaseModel):
    extension_uuid: UUID
    extension_name: str
    platform: str
    creation_datetime: datetime

