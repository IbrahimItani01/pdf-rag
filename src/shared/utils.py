import os
import uuid
import tiktoken
import psycopg2
from src.shared.constants import embedding_supported_model,empty_page_threshold,overlap_tokens_count,file_total_token_limit
from src.shared.utils import get_env_variable
from fastapi import HTTPException
from typing import List, Any

def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        print(f"{var_name} not found")
        raise HTTPException(status_code=400,detail=f"{var_name} not found")
    return value.strip()

def generate_file_uuid()->int:
    return uuid.uuid4()

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