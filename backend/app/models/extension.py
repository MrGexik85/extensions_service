from pydantic import BaseModel
from fastapi import File


class Extension(BaseModel):
    file: File 