import re
from fastapi import HTTPException
from src.models.requests import UserRegisterRequest

def validate_user_register_data(data: UserRegisterRequest):
    errors = {}
    
    # Validate user_name
    if not data.user_name or not data.user_name.strip():
        errors["user_name"] = "Username is required"
    elif len(data.user_name.strip()) < 3:
        errors["user_name"] = "Username must be at least 3 characters long"
    elif len(data.user_name.strip()) > 50:
        errors["user_name"] = "Username must not exceed 50 characters"
    elif not re.match(r"^[a-zA-Z0-9_-]+$", data.user_name.strip()):
        errors["user_name"] = "Username can only contain letters, numbers, underscores, and hyphens"
    
    # Validate user_email
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not data.user_email or not data.user_email.strip():
        errors["user_email"] = "Email is required"
    elif not re.match(email_pattern, data.user_email.strip()):
        errors["user_email"] = "Invalid email format"
    elif len(data.user_email.strip()) > 254:
        errors["user_email"] = "Email must not exceed 254 characters"
    
    # Validate user_password (based on Supabase requirements from image)
    if not data.user_password:
        errors["user_password"] = "Password is required"
    else:
        if len(data.user_password) < 10:
            errors["user_password"] = "Password must be at least 10 characters long"
        elif not (re.search(r"[a-z]", data.user_password) and 
                  re.search(r"[A-Z]", data.user_password) and 
                  re.search(r"\d", data.user_password) and 
                  re.search(r"[!@#$%^&*(),.?\":{}|<>~`_+=\[\]\\;'-]", data.user_password)):
            errors["user_password"] = "Password must contain at least one lowercase letter, uppercase letter, digit, and symbol"
    
    # Validate user_openai_api_key
    if not data.user_openai_api_key or not data.user_openai_api_key.strip():
        errors["user_openai_api_key"] = "OpenAI API key is required"
    elif not data.user_openai_api_key.strip().startswith("sk-"):
        errors["user_openai_api_key"] = "Invalid OpenAI API key format (must start with 'sk-')"
    elif len(data.user_openai_api_key.strip()) < 40:
        errors["user_openai_api_key"] = "OpenAI API key appears to be too short"
    
    # Throw HTTPException if any validation errors
    if errors:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Validation failed",
                "errors": errors
            }
        )