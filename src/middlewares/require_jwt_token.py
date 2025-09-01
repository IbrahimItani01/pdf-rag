import requests
from datetime import datetime,timezone
from fastapi import Request, HTTPException
from jose import jwt
from src.shared.utils import get_env_variable
from src.models.requests import UserInfoFromJWT
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
    sub = decoded["sub"]
    session_id = decoded["session_id"]
    role = decoded["role"]
    email = decoded["email"]
    if not exp:
        raise HTTPException(status_code=401, detail="Token missing expiry claim")
    
    if datetime.now(timezone.utc) > datetime.fromtimestamp(exp, tz=timezone.utc):
        raise HTTPException(status_code=419, detail="Session expired")
    
    # Return decoded user info for endpoint usage
    return {
        "user_id":sub,
        "email":email,
        "session_id":session_id,
        "role":role
    }
   