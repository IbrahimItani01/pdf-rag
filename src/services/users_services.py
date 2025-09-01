from fastapi import Request, HTTPException
from src.models.requests import UserRegisterRequest,UserLoginRequest
from src.models.responses import UserRegisterResponse,UserLoginResponse
from src.services.gateway_services import supabase_client,fernet
from src.shared.constants import email_confirm_redirect_url
from src.shared.env import get_env_variable

def register_user(request: Request, user: UserRegisterRequest) -> UserRegisterResponse:
    try: 
        encrypted_openai_key = fernet.encrypt(user.user_openai_api_key.encode()).decode()
        data = supabase_client.auth.sign_up({
            "email": user.user_email,
            "password": user.user_password,
            "options": {
                "data": {
                    "user_name": user.user_name,
                    "user_openai_key": encrypted_openai_key,
                },
                "email_redirect_to": email_confirm_redirect_url
            }
        })

        # Extract the user and session
        user_obj = data.user
        session = data.session

        # Determine token
        user_token = session["access_token"] if session else None

        # Build response message
        message = "User registered successfully." if session else "User registered successfully. Please check your email to confirm registration."

        return UserRegisterResponse(
            message=message,
            user_token=user_token,
            version=request.app.version
        )

    except Exception as e:
        print(f"Error while registering user: {e}")
        raise HTTPException(status_code=500, detail=f"Error while registering user: {e}")

def login_user(request: Request, user: UserLoginRequest) -> UserLoginResponse:
    try:
        response = supabase_client.auth.sign_in_with_password(
        {
            "email": user.user_email,
            "password": user.user_password,
        })
        user_token=response.session.access_token
        refresh_token=response.session.refresh_token
        user_metadata=response.session.user.user_metadata
        return UserLoginResponse(
            message="User Logged In Successfully",
            user_token=user_token,
            refresh_token=refresh_token,
            openai_api_key=user_metadata["user_openai_key"],
            user_name=user_metadata["user_name"],
            version=request.app.version
        )
    except Exception as e:
        print(f"Error Logging In User: {e}")
        raise HTTPException(status_code=500,detail=f"Error Logging In User: {e}")