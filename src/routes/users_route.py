from fastapi import APIRouter, Request, Depends
from src.models.requests import UserRegisterRequest
from src.services.users_services import register_user
from src.middlewares.verify_api_key import verify_api_key
from src.models.responses import UserRegisterResponse

router = APIRouter(
    prefix="/users",       
    tags=["Users"],         
    dependencies=[Depends(verify_api_key)]  
)

@router.post("/register", response_model=UserRegisterRequest)
async def upload_file(
    request: Request,
    user_data: UserRegisterRequest,
    
):
    return register_user(request,user_data)
