from fastapi import Request
from src.models.requests import UserRegisterRequest
from src.models.responses import UserRegisterResponse
def register_user(request: Request, user: UserRegisterRequest) -> UserRegisterResponse:
    return {
        "message": "User registered successfully",
        "user_token": "12313",
        "version": request.app.version
    }
