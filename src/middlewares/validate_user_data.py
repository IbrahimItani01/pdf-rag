import re
from fastapi import HTTPException
from src.models.requests import UserRegisterRequest
 
def validate_user_register_data(user_data: UserRegisterRequest):
    errors = {}
    
    # Validate user_name
    if not user_data.user_name or not user_data.user_name.strip():
        errors["user_name"] = "Username is required"
    elif len(user_data.user_name.strip()) < 3:
        errors["user_name"] = "Username must be at least 3 characters long"
    elif len(user_data.user_name.strip()) > 50:
        errors["user_name"] = "Username must not exceed 50 characters"
    elif not re.match(r"^[a-zA-Z0-9_-]+$", user_data.user_name.strip()):
        errors["user_name"] = "Username can only contain letters, numbers, underscores, and hyphens"
    
    # Validate user_email
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not user_data.user_email or not user_data.user_email.strip():
        errors["user_email"] = "Email is required"
    elif not re.match(email_pattern, user_data.user_email.strip()):
        errors["user_email"] = "Invalid email format"
    elif len(user_data.user_email.strip()) > 254:
        errors["user_email"] = "Email must not exceed 254 characters"
    
    # Validate user_password (based on Supabase requirements from image)
    if not user_data.user_password:
        errors["user_password"] = "Password is required"
    else:
        if len(user_data.user_password) < 10:
            errors["user_password"] = "Password must be at least 10 characters long"
        elif not (re.search(r"[a-z]", user_data.user_password) and 
                  re.search(r"[A-Z]", user_data.user_password) and 
                  re.search(r"\d", user_data.user_password) and 
                  re.search(r"[!@#$%^&*(),.?\":{}|<>~`_+=\[\]\\;'-]", user_data.user_password)):
            errors["user_password"] = "Password must contain at least one lowercase letter, uppercase letter, digit, and symbol"
    
    # Validate user_openai_api_key
    if not user_data.user_openai_api_key or not user_data.user_openai_api_key.strip():
        errors["user_openai_api_key"] = "OpenAI API key is required"
    
    # Throw HTTPException if any validation errors
    if errors:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Validation failed",
                "errors": errors
            }
        )
    return user_data