import uuid
import tiktoken
import psycopg2
import requests
from fastapi import HTTPException,Request,Response
from typing import List, Any
from jose import jwt
from src.shared.constants import embedding_supported_model,empty_page_threshold,overlap_tokens_count,file_total_token_limit,base_prompt
from src.services.gateway_services import fernet,supabase_client
from src.services.gateway_services import return_openai_client
from src.shared.env import get_env_variable
from src.models.requests import UserInfoFromJWT

def generate_file_uuid()->int:
    return uuid.uuid4()

def build_prompt(question: str, context_chunks: List[str]) -> str:
    """
    Build a prompt for the LLM given a question and retrieved context.
    """
    context_text = "\n".join(context_chunks) if context_chunks else "No relevant context found."
    return base_prompt.format(question=question, context=context_text)

def tokenize_document(document : List[Any]) -> int:
    try:
        # Get the encoding for the supported model
        enc = tiktoken.encoding_for_model(model_name=embedding_supported_model)
        
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
    
def is_scanned_or_empty(documents, empty_threshold: float = 0.05) -> bool:
    if not documents:
        return True

    total_pages = len(documents)
    empty_pages = 0

    for doc in documents:
        text = doc.page_content.strip()
        if len(text) < empty_page_threshold:  
            empty_pages += 1

    empty_ratio = empty_pages / total_pages
    return empty_ratio >= empty_threshold

def chunk_document_by_tokens(documents: List[Any], max_tokens: int = file_total_token_limit, overlap_tokens: int = overlap_tokens_count) -> List[dict]:
    from tiktoken import encoding_for_model
    from src.shared.utils import embedding_supported_model

    # Combine all text into a single string
    full_text = " ".join([doc.page_content for doc in documents if hasattr(doc, 'page_content') and doc.page_content])

    # Tokenize full text
    enc = encoding_for_model(model_name=embedding_supported_model)
    tokens = enc.encode(full_text)

    chunks = []
    start = 0
    total_tokens = len(tokens)

    while start < total_tokens:
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append({
            "content": chunk_text,
            "token_count": len(chunk_tokens)
        })
        start = end - overlap_tokens
        if start < 0:
            start = 0

    return chunks

def query_cursor(query: str):
    USER = get_env_variable("DB_USER")
    PASSWORD = get_env_variable("DB_PASSWORD")
    HOST = get_env_variable("DB_HOST")
    PORT = get_env_variable("DB_PORT")
    DBNAME = get_env_variable("DB_NAME")

    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        
        cursor = connection.cursor()
        cursor.execute(query)

        # If the query returns rows, fetch them
        if cursor.description:  # cursor.description is None if it's an INSERT/UPDATE/DELETE
            result = cursor.fetchall()
        else:
            result = None
            connection.commit()  # commit if it was a write operation

        cursor.close()
        connection.close()

        return result

    except Exception as e:
        print(f"Failed to connect to DB: {e}")
        return None
    
def decrypt_encryption (encryption: str) -> str:
    return fernet.decrypt(encryption.encode()).decode()

def create_embedding_for_chunk(content: str, user_info: UserInfoFromJWT) -> List[float]:
    """
    Create embedding for a text chunk
    """
    try:
        encrypted_openai_key = user_info['user_openai_key']
        decrypted_openai_key = decrypt_encryption(encryption=encrypted_openai_key)
        openai_client = return_openai_client(decrypted_openai_key)
        response = openai_client.embeddings.create(
            input=content,
            model=embedding_supported_model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error creating embedding: {e}")
        error_msg = str(e)
        if "401" in error_msg or "invalid_api_key" in error_msg:
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key")
        elif "429" in error_msg:
            raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded")
        elif "quota" in error_msg.lower():
            raise HTTPException(status_code=402, detail="OpenAI API quota exceeded")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to create embedding: {error_msg}")
        
def query_user_refresh_token(user_id:str):
    try:
        response = supabase_client.table("users").select("refresh_token").eq("id",user_id).execute()
        return response.data[0].refresh_token
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Failed to query refresh token: {e}")
    
def update_user_refresh_token_in_db(user_id: str, refresh_token:str):
    try:
        response = supabase_client.table("users").update({"refresh_token":refresh_token}).eq("id",user_id).execute
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Failed to update refresh token in user's row in DB: {e}")
    
def add_refresh_token_headers(request: Request, response: Response) -> None:
    """Utility function to add refresh token headers if token was refreshed"""
    if hasattr(request.state, 'token_refresh_info') and request.state.token_refresh_info.token_was_refreshed:
        response.headers["X-New-Access-Token"] = request.state.token_refresh_info.new_access_token
        response.headers["X-Token-Refreshed"] = "true"