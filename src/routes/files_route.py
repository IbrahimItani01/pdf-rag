from fastapi import APIRouter, Request, Depends, UploadFile
from src.services.upload_file_service import process_pdf_file
from src.middlewares.verify_api_key import verify_api_key
from src.middlewares.validate_upload_file import validate_uploaded_file
from src.models.responses import UploadFileResponse

router = APIRouter(
    prefix="/files",       
    tags=["Files"],         
    dependencies=[Depends(verify_api_key)]  
)

@router.post("/upload", response_model=UploadFileResponse)
async def upload_file(
    request: Request,
    file: UploadFile = Depends(validate_uploaded_file),
):
    return process_pdf_file(request, file)
