"""
Helper utilities
"""
import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException
from typing import Optional
from ..core.config import settings


def generate_task_id() -> str:
    """Generate a unique task ID"""
    return f"task_{uuid.uuid4().hex}"


def generate_file_id() -> str:
    """Generate a unique file ID"""
    return f"file_{uuid.uuid4().hex}"


async def save_upload_file(upload_file: UploadFile, custom_filename: Optional[str] = None) -> str:
    """
    Save an uploaded file to disk
    Returns: file path
    """
    # Validate file extension
    file_ext = os.path.splitext(upload_file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Create upload directory if not exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate filename
    if custom_filename:
        filename = custom_filename
    else:
        file_id = generate_file_id()
        filename = f"{file_id}{file_ext}"
    
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await upload_file.read()
        
        # Check file size
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
        
        await f.write(content)
    
    return file_path


def cleanup_file(file_path: str) -> bool:
    """Delete a file safely"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def validate_language_pair(source_lang: str, target_lang: str) -> bool:
    """Validate if the language pair is supported"""
    if source_lang == target_lang:
        raise HTTPException(
            status_code=400,
            detail="Source and target languages cannot be the same"
        )
    return True
