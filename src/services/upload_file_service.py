import os
import tempfile
from fastapi import UploadFile, Request
from langchain_community.document_loaders import PyPDFLoader
from src.shared.constants import supported_model
from src.shared.utils import tokenize_document

def process_pdf_file(request: Request,file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file.file.read())
        temp_file_path = temp_file.name
    try:
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        total_pages = documents[0].metadata['total_pages']
        token_count = tokenize_document(documents)

        return {"message": "PDF processed successfully", "metadata":{"pages": total_pages, "token_count": token_count} ,"version": request.app.version }
    
    finally:
        os.unlink(temp_file_path)