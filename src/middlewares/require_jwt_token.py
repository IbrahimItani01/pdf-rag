import requests
from fastapi import Request, HTTPException
from jose import jwt
from src.shared.utils import get_signing_key

def validate_jwt_and_session(request: Request):
    """Global dependency: validates JWT signature and session expiry"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = auth_header.split(" ")[1]
    
    try:
        signing_key = get_signing_key(token)
        decoded = jwt.decode(token, signing_key, algorithms=["RS256"], options={"verify_aud": False})
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Validate session expiry
    exp = decoded.get("exp")
    if not exp:
        raise HTTPException(status_code=401, detail="Token missing expiry claim")
    
    if datetime.now(timezone.utc) > datetime.fromtimestamp(exp, tz=timezone.utc):
        raise HTTPException(status_code=419, detail="Session expired")
    
    # Return decoded user info for endpoint usage
    return {
        "user_id": decoded.get("sub"),
        "email": decoded.get("email"),
        "session_id": decoded.get("session_id"),
        "role": decoded.get("role")
    }