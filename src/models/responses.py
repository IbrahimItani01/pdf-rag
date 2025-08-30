from pydantic import BaseModel

class ProcessingMetadata(BaseModel):
    pages: int
    token_count: int
    chunks_stored: int
    file_id: str

class UploadFileResponse(BaseModel):
    message: str
    metadata: ProcessingMetadata
    version: str

class HealthResponse(BaseModel):
    message: str
    version: str
    title: str
    description: str
