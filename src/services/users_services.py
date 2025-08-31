from fastapi import Request, HTTPException
from src.models.requests import UserRegisterRequest
from src.models.responses import UserRegisterResponse
from src.services.gateway_services import supabase_client
from src.shared.constants import email_confirm_redirect_url
 
def register_user(request: Request, user: UserRegisterRequest) -> UserRegisterResponse:
    try: 
        data = supabase_client.auth.sign_up({
            "email": user.user_email,
            "password": user.user_password,
            "options": {
                "data": {
                    "user_name": user.user_name,
                    "user_openai_key": user.user_openai_api_key,
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
