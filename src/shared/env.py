import os
from fastapi import HTTPException

def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        print(f"{var_name} not found")
        raise HTTPException(status_code=400,detail=f"{var_name} not found")
    return value.strip()