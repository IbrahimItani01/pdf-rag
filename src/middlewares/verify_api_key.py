from fastapi import Request, Depends, HTTPException
from fastapi.security import APIKeyHeader
from src.shared.utils import get_env_variable

api_key_header = APIKeyHeader(name="x-api-key",auto_error=False,description="An authentication for APIs using api key")

async def verify_api_key(api_key: str = Depends(api_key_header)):  
    if api_key is None: 
        raise HTTPException(status_code=401,detail="Missing API Key")
    if api_key != get_env_variable("X_API_KEY"):
        raise HTTPException(status_code=401,detail="Invalid API Key")
    
