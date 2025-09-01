from pydantic import BaseModel

class UserRegisterRequest(BaseModel):
    user_name: str
    user_email: str
    user_password: str 
    user_openai_api_key: str
    
class UserLoginRequest(BaseModel):
    user_email: str
    user_password: str
    
class UserInfoFromJWT(BaseModel):
    user_id: str
    email: str
    session_id: str
    role:str
    user_name: str
    user_openai_key: str
