from fastapi import APIRouter, Request, Depends
from src.models.requests import UserRegisterRequest,UserLoginRequest,UserInfoFromJWT
from src.services.users_services import register_user,login_user,delete_user_account
from src.middlewares.verify_api_key import verify_api_key
from src.middlewares.validate_user_data import validate_user_register_data
from src.middlewares.require_jwt_token import validate_jwt_and_session
from src.models.responses import UserRegisterResponse, UserLoginResponse,AccountDeleteResponse

router = APIRouter(
    prefix="/users",       
    tags=["Users"],         
    dependencies=[Depends(verify_api_key)]  
)

@router.post("/register", response_model=UserRegisterResponse)
async def register_user_endpoint(
    request: Request,
    user_data: UserRegisterRequest = Depends(validate_user_register_data),
):
    return register_user(request,user_data)

@router.post("/login", response_model=UserLoginResponse)
async def login_user_endpoint(
    request: Request,
    user_data: UserLoginRequest,
):
    return login_user(request,user_data)

@router.post("/delete-account", response_model=AccountDeleteResponse)
async def delete_account_endpoint(
    request: Request,
    user_info: UserInfoFromJWT = Depends(validate_jwt_and_session),
):
    return delete_user_account(request,user_info)