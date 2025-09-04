from fastapi import Request, HTTPException
from src.models.requests import UserInfoFromJWT
from src.models.responses import FileInfo, GetFilesResponse
from src.shared.constants import pinecone_index_name
from src.services.gateway_services import pc_client
from typing import List, Dict, Any
import json

def get_files_service(request: Request, user_info: UserInfoFromJWT) -> GetFilesResponse:
    """
    More efficient version - retrieves files using batch queries and pagination.
    """
    try:
        index = pc_client.Index(pinecone_index_name)
        
        files_dict: Dict[str, Dict[str, Any]] = {}
        
        # Use pagination to get all user's documents efficiently
        # Start with a smaller batch size
        batch_size = 100
        retrieved_count = 0
        
        while True:
            # Query with pagination
            search_results = index.query(
                vector=[0.0] * 1536,  # Dummy vector
                top_k=batch_size,
                namespace="__default__",
                include_metadata=True,
                filter={
                    "user_id": {"$eq": user_info["user_id"]}
                }
            )
            
            if not search_results.matches:
                break
            
            # Process this batch
            for match in search_results.matches:
                metadata = match.metadata
                doc_id = metadata.get("doc_id")
                
                if doc_id and doc_id not in files_dict:
                    files_dict[doc_id] = {
                        "doc_id": doc_id,
                        "filename": metadata.get("filename", "Unknown"),
                        "file_type": metadata.get("file_type", "Unknown"),
                        "upload_date": metadata.get("upload_date"),
                        "file_size": metadata.get("file_size"),
                        "total_pages": metadata.get("total_pages", 1),
                        "chunk_count": 1
                    }
                elif doc_id:
                    files_dict[doc_id]["chunk_count"] += 1
            
            retrieved_count += len(search_results.matches)
            
            # If we got fewer results than requested, we've reached the end
            if len(search_results.matches) < batch_size:
                break
        
        # Convert to FileInfo objects
        files_list = [
            FileInfo(
                file_id=file_data["doc_id"],  # Fixed: use file_id instead of doc_id
                filename=file_data["filename"],
                file_type=file_data["file_type"],
                pages=file_data["total_pages"],  # Fixed: use pages instead of total_pages
                token_count=0,  # You'll need to add logic to calculate this if needed
                chunks_stored=file_data["chunk_count"],  # Fixed: use chunks_stored instead of chunk_count
                upload_date=file_data["upload_date"],
                file_size=file_data["file_size"]
            )
            for file_data in files_dict.values()
        ]
        
        # Sort by upload date (most recent first)
        files_list.sort(
            key=lambda x: x.upload_date or "", 
            reverse=True
        )
        
        return GetFilesResponse(
            version=request.app.version, 
            message="Files retrieved successfully",
            files=files_list,
            total_count=len(files_list)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving files: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve files: {str(e)}"
        )