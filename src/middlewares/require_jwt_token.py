import requests
from datetime import datetime,timezone
from fastapi import Request, HTTPException
from jose import jwt
from src.shared.env import get_env_variable
from src.shared.utils import query_user_refresh_token,update_user_refresh_token_in_db
from src.services.gateway_services import supabase_client
from src.models.requests import UserInfoFromJWT

class TokenRefreshInfo:
    """Class to store token refresh information across the request lifecycle"""
    def __init__(self):
        self.new_access_token = None
        self.token_was_refreshed = False
        
def validate_jwt_and_session(request: Request) -> UserInfoFromJWT:
    """Global dependency: validates JWT signature and session expiry"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = auth_header.split(" ")[1]
    
    try:
        signing_key = get_env_variable("SUPABASE_SIGNING_KEY")
        decoded = jwt.decode(token, signing_key, algorithms=["HS256"], options={"verify_aud": False})
    except jwt.JWTError as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid token")
    
    exp = decoded["exp"]
    user_id = decoded["sub"]
    session_id = decoded["session_id"]
    role = decoded["role"]
    email = decoded["email"]
    openai_key = decoded["user_metadata"]["user_openai_key"]
    user_name = decoded["user_metadata"]["user_name"]
    
    if not exp:
        raise HTTPException(status_code=401, detail="Token missing expiry claim")
    
    refresh_info = TokenRefreshInfo()
    
    if datetime.now(timezone.utc) > datetime.fromtimestamp(exp, tz=timezone.utc):
        try:
            user_refresh_token = query_user_refresh_token(user_id)
            new_session = retrieve_new_session(user_refresh_token)
            
            update_user_refresh_token_in_db(user_id, new_session["refresh_token"])
            
            refresh_info.new_access_token = new_session["access_token"]
            refresh_info.token_was_refreshed = True
            
            new_decoded = jwt.decode(
                new_session["access_token"], 
                signing_key, 
                algorithms=["HS256"], 
                options={"verify_aud": False}
            )
            
            user_id = new_decoded["sub"]
            session_id = new_decoded["session_id"]
            role = new_decoded["role"]
            email = new_decoded["email"]
            openai_key = new_decoded["user_metadata"]["user_openai_key"]
            user_name = new_decoded["user_metadata"]["user_name"]
            
        except Exception as e:
            print(f"Token refresh failed: {e}")
            raise HTTPException(status_code=401, detail=f"Session expired and refresh failed: {e}")
    
    request.state.token_refresh_info = refresh_info
    
    return {
        "user_id": user_id,
        "email": email,
        "session_id": session_id,
        "role": role,
        "user_openai_key": openai_key,
        "user_name": user_name
    }
   
def retrieve_new_session(refresh_token:str):
    try:
        response = supabase_client.auth.refresh_session(refresh_token=refresh_token)
        return {"access_token":response.session.access_token,"refresh_token":response.session.refresh_token}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Failed to refresh session: {e}")
