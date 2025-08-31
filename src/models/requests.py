from pydantic import BaseModel

class UserRegisterRequest(BaseModel):
    user_name: str
    user_email: str
    user_password: str 
    user_openai_api_key: str