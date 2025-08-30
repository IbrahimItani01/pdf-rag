import os
import tiktoken
from src.shared.constants import supported_model
from fastapi import HTTPException
from typing import List, Any

def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        print(f"{var_name} not found")
        raise HTTPException(status_code=400,detail=f"{var_name} not found")
    return value.strip()

def tokenize_document(document : List[Any]) -> int:
    try:
        # Get the encoding for the supported model
        enc = tiktoken.encoding_for_model(model_name=supported_model)
        
        total_tokens = 0
        
        # Process each page in the document
        for page in document:
            if hasattr(page, 'page_content') and page.page_content:
                # Encode the page content and count tokens
                tokens = enc.encode(page.page_content)
                total_tokens += len(tokens)
        
        return total_tokens
        
    except Exception as e:
        print(f"Error tokenizing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error tokenizing document: {str(e)}")