import os
import tempfile
from fastapi import UploadFile, Request,HTTPException
from langchain_community.document_loaders import PyPDFLoader
from src.shared.utils import tokenize_document,generate_file_uuid,is_scanned_or_empty,chunk_document_by_tokens
from src.shared.constants import file_total_token_limit

def process_pdf_file(request: Request,file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file.file.read())
        temp_file_path = temp_file.name
    try:
        file_uuid = generate_file_uuid()
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        
        if is_scanned_or_empty(documents):
            raise HTTPException(status_code=422, detail="File is scanned or empty")
        
        total_pages = documents[0].metadata['total_pages']
        token_count = tokenize_document(documents)
        if token_count > file_total_token_limit:
            chunks = chunk_document_by_tokens(documents)
            print(chunks[0]["token_count"])
            print(chunks[1]["token_count"])
            print(f"PDF split into {len(chunks)} chunks, each <= {file_total_token_limit} tokens.")

        return {"message": "PDF processed successfully", "metadata":{"pages": total_pages, "token_count": token_count} ,"version": request.app.version }
    
    finally:
        os.unlink(temp_file_path)