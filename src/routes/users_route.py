from fastapi import APIRouter, Request, Depends
from src.models.requests import UserRegisterRequest,UserLoginRequest
from src.services.users_services import register_user,login_user
from src.middlewares.verify_api_key import verify_api_key
from src.middlewares.validate_user_data import validate_user_register_data
from src.models.responses import UserRegisterResponse, UserLoginResponse

router = APIRouter(
    prefix="/users",       
    tags=["Users"],         
    dependencies=[Depends(verify_api_key)]  
)

@router.post("/register", response_model=UserRegisterResponse)
async def upload_file(
    request: Request,
    user_data: UserRegisterRequest = Depends(validate_user_register_data),
):
    return register_user(request,user_data)

@router.post("/login", response_model=UserLoginResponse)
async def upload_file(
    request: Request,
    user_data: UserLoginRequest,
):
    return login_user(request,user_data)