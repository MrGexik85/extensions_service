from typing import List
from pydantic import BaseModel

from .extension import Extension

class UserWithExtensionsResponse(BaseModel):
    user_uuid: str
    extensions: List[Extension] = []
