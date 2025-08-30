from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends,dependencies,UploadFile,Request
from src.shared.constants import version,title,description
from src.services.upload_file_service import process_pdf_file
from src.services.health_service import get_server_health
from src.middlewares.verify_api_key import verify_api_key
from src.middlewares.validate_upload_file import validate_uploaded_file
from src.models.responses import HealthResponse,UploadFileResponse

app = FastAPI(version=version,title=title,description=description)

@app.get("/health",response_model=HealthResponse)
async def root(request: Request):
    return get_server_health(request)

@app.post("/upload",response_model=UploadFileResponse)
async def upload_file(request: Request,file: UploadFile = Depends(validate_uploaded_file),_: None = Depends(verify_api_key)):
    return process_pdf_file(request,file)
