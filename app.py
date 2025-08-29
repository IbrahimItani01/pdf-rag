from fastapi import FastAPI
from src.shared.constants import version
from src.services.upload_file_service import process_pdf_file
from src.models.upload_file_models import UploadFileRequest

app = FastAPI()

@app.get("/health")
async def root():
    return {"message": "Server running","version":version}

@app.post("/upload")
async def upload_file(request: UploadFileRequest):
    return process_pdf_file()