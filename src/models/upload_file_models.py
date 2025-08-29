from pydantic import BaseModel
from fastapi import UploadFile

class UploadFileRequest(BaseModel):
    file: UploadFile