from pydantic import BaseModel

class ProcessingMetadata(BaseModel):
    pages: int
    token_count: int

class UploadFileResponse(BaseModel):
    message: str
    metadata: ProcessingMetadata
    version: str

class HealthResponse(BaseModel):
    message: str
    version: str
    title: str
    description: str
