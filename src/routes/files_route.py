from fastapi import APIRouter, Request, Depends, UploadFile, Response
from src.services.upload_file_service import process_pdf_file
from src.services.query_file_services import process_file_query
from src.middlewares.verify_api_key import verify_api_key
from src.middlewares.validate_upload_file import validate_uploaded_file
from src.middlewares.require_jwt_token import validate_jwt_and_session
from src.models.responses import UploadFileResponse,QueryFileResponse
from src.models.requests import UserInfoFromJWT,QueryFileRequest
from src.shared.utils import add_refresh_token_headers

router = APIRouter(
    prefix="/files",       
    tags=["Files"],         
    dependencies=[Depends(verify_api_key)]  # Removed validate_jwt_and_session from here
)

@router.post("/upload", response_model=UploadFileResponse)
async def upload_file(
    request: Request,
    response: Response,
    user_info: UserInfoFromJWT = Depends(validate_jwt_and_session),
    file: UploadFile = Depends(validate_uploaded_file),
):
    result = process_pdf_file(request, file, user_info)
    
    add_refresh_token_headers(request, response)
    
    return result

@router.post("/query", response_model=QueryFileResponse)
async def query_file(
    request: Request,
    response: Response,
    query_info: QueryFileRequest,
    user_info: UserInfoFromJWT = Depends(validate_jwt_and_session),
):
    result = process_file_query(request, query_info, user_info)
    
    add_refresh_token_headers(request, response)
    
    return result