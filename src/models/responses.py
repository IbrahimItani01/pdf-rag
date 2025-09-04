from pydantic import BaseModel
from typing import List, Optional
class ProcessingMetadata(BaseModel):
    pages: int
    token_count: int
    chunks_stored: int
    file_id: str

class UploadFileResponse(BaseModel):
    message: str
    metadata: ProcessingMetadata
    version: str

class FileInfo(BaseModel):
    """Dedicated model for file listing - cleaner separation of concerns"""
    file_id: str
    filename: str
    file_type: str
    pages: int
    token_count: int
    chunks_stored: int
    upload_date: Optional[str] = None
    file_size: Optional[int] = None
class GetFilesResponse(BaseModel):
    version: str
    message: str
    files: List[FileInfo]  # Use FileInfo instead of ProcessingMetadata
    total_count: int
class Source(BaseModel):
    doc_id: str
    page: int

class QueryFileResponse(BaseModel):
    answer: str
    sources: List[Source]
class UserRegisterResponse(BaseModel):
    message: str
    user_token: str | None
    version: str

class UserLoginResponse(BaseModel):
    message: str
    user_token: str
    version: str
    openai_api_key: str
    user_name: str
    refresh_token: str

class AccountDeleteResponse(BaseModel):
    message: str
    version: str

class HealthResponse(BaseModel):
    message: str
    version: str
    title: str
    description: str
