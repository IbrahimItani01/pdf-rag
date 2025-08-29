from fastapi import UploadFile
from fastapi import HTTPException
from src.shared.constants import allowed_file_extensions, allowed_file_size
async def validate_uploaded_file(file: UploadFile ):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_extension = file.filename.lower().split('.')[-1]
    
    if f".{file_extension}" not in allowed_file_extensions:
        raise HTTPException(
            status_code=422, 
            detail=f"File type not allowed, and can't be processed. Allowed types: {', '.join(allowed_file_extensions)}"
        )
        
    file.file.seek(0, 2)  # Seek to end of file
    file_size = file.file.tell()  # Get current position (file size)
    file.file.seek(0)  # Reset to beginning
    
    if file_size > allowed_file_size:
        raise HTTPException(
            status_code=422,
            detail=f"File too large. Maximum size: {allowed_file_size // (1024*1024)}MB"
        )
    
    if file_extension == "pdf":
        file_header = await file.read(4)
        await file.seek(0)  
        if file_header != b'%PDF':
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file format"
            )
    return file