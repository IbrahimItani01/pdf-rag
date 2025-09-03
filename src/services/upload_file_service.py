import os
import tempfile
from typing import List, Dict
from fastapi import UploadFile, Request, HTTPException
from src.services.gateway_services import return_openai_client, pc_client, fernet
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.shared.utils import tokenize_document, generate_file_uuid, is_scanned_or_empty, decrypt_encryption, create_embedding_for_chunk
from src.shared.constants import file_total_token_limit, pinecone_index_name
from src.models.requests import UserInfoFromJWT

def process_pdf_file(request: Request, file: UploadFile, user_info: UserInfoFromJWT):
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
        chunks = documents
        
        if token_count > file_total_token_limit:
            # Use LangChain’s semantic-aware splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,   # adjust depending on your needs
                chunk_overlap=200  # overlap helps keep context
            )
            chunks = text_splitter.split_documents(documents)
            print(f"PDF split into {len(chunks)} semantic chunks using RecursiveCharacterTextSplitter.")

        stored_chunks = store_chunks_with_embeddings(chunks, file_uuid, file.filename, user_info=user_info)
        
        return {
            "message": "PDF processed successfully", 
            "metadata": {
                "pages": total_pages, 
                "token_count": token_count,
                "chunks_stored": len(stored_chunks),
                "file_id": str(file_uuid)
            },
            "version": request.app.version
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in process_pdf_file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
    finally:
        os.unlink(temp_file_path)

def store_chunks_with_embeddings(chunks: List, doc_id: str, filename: str, user_info: UserInfoFromJWT) -> List[Dict]:
    index = pc_client.Index(pinecone_index_name)
    vectors_to_upsert = []
    stored_chunks = []
    
    for chunk_index, chunk in enumerate(chunks):
        try:
            # Extract content and metadata from chunk
            if hasattr(chunk, 'page_content'):
                content = chunk.page_content
                page_num = chunk.metadata.get('page', chunk_index + 1)
            else:
                content = chunk.get("content", "")
                page_num = chunk.get("page", chunk_index + 1)
            
            # Normalize casing for embeddings
            content_lower = content.lower().strip()

            embedding = create_embedding_for_chunk(content_lower, user_info=user_info)
            
            vector_id = f"{user_info['user_id']}_{doc_id}_{chunk_index}"
            
            metadata = {
                "doc_id": str(doc_id),
                "filename": filename,
                "page_num": page_num,
                "chunk_index": chunk_index,
                "original_text": content[:1000],   # preserve original case for display
                "token_count": len(content.split()) * 1.3, 
                "user_id": user_info["user_id"]
            }
            
            vectors_to_upsert.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })
            
            stored_chunks.append({
                "chunk_index": chunk_index,
                "vector_id": vector_id,
                "page_num": page_num
            })
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error processing chunk {chunk_index}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process chunk {chunk_index}: {str(e)}")
    
    if not vectors_to_upsert:
        raise HTTPException(status_code=500, detail="No chunks were successfully processed")
    
    try:
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            index.upsert(vectors=batch)
            print(f"Upserted batch {i//batch_size + 1} with {len(batch)} vectors")
    except Exception as e:
        print(f"Error upserting to Pinecone: {e}")
        raise HTTPException(status_code=500, detail="Failed to store embeddings in Pinecone")
    
    return stored_chunks
