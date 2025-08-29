from fastapi import FastAPI, Depends
from src.shared.constants import version,title,description
from src.services.upload_file_service import process_pdf_file
from src.models.upload_file_models import UploadFileRequest
from src.middlewares.verify_api_key import verify_api_key

app = FastAPI(version=version,title=title,description=description)

@app.get("/health")
async def root():
    return {"message": "Server running","version":version}

@app.post("/upload",dependencies==[Depends(verify_api_key)])
async def upload_file(request: UploadFileRequest):
    return process_pdf_file()