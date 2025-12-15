"""
Translation Routes
"""
from fastapi import APIRouter, File, UploadFile, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from typing import Dict
from ..models.request import TranslateRequest, DocumentTranslateRequest
from ..models.response import (
    TranslateResponse, 
    TaskResponse, 
    TaskStatusResponse,
    DataResponse,
    StatusEnum
)
from ..core.security import get_current_user
from ..services.translation_service import translation_service
from ..utils.helpers import save_upload_file, generate_task_id, cleanup_file
import asyncio
from datetime import datetime

router = APIRouter(prefix="/translate", tags=["Translation"])

# In-memory task storage (use Redis in production)
tasks_storage: Dict[str, dict] = {}


async def process_translation_task(task_id: str, file_path: str, source_lang: str, target_lang: str, use_cloud: bool):
    """Background task to process document translation"""
    try:
        tasks_storage[task_id]["status"] = StatusEnum.PROCESSING
        tasks_storage[task_id]["progress"] = 10
        
        # Simulate processing delay
        await asyncio.sleep(2)
        tasks_storage[task_id]["progress"] = 50
        
        # Perform translation
        output_path = await translation_service.translate_document(
            file_path, source_lang, target_lang, use_cloud
        )
        
        tasks_storage[task_id]["status"] = StatusEnum.COMPLETED
        tasks_storage[task_id]["progress"] = 100
        tasks_storage[task_id]["result"] = {
            "output_file": output_path,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        tasks_storage[task_id]["updated_at"] = datetime.utcnow()
        
    except Exception as e:
        tasks_storage[task_id]["status"] = StatusEnum.FAILED
        tasks_storage[task_id]["error"] = str(e)
        tasks_storage[task_id]["updated_at"] = datetime.utcnow()
        cleanup_file(file_path)


@router.post("/text", response_model=DataResponse)
async def translate_text(
    request: TranslateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Translate text
    
    - **text**: Text to translate (max 10,000 characters)
    - **source_lang**: Source language code
    - **target_lang**: Target language code  
    - **use_cloud**: Use Azure cloud translation (true) or local model (false)
    """
    result = await translation_service.translate_text(
        request.text,
        request.source_lang.value,
        request.target_lang.value,
        request.use_cloud
    )
    
    response = TranslateResponse(**result)
    
    return DataResponse(
        code=200,
        message="Translation completed successfully",
        data=response.dict()
    )


@router.post("/document", response_model=TaskResponse)
async def translate_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Document file to translate"),
    source_lang: str = "zh-Hans",
    target_lang: str = "en",
    use_cloud: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Translate a document file (async)
    
    Supported formats: .docx, .pptx, .xlsx, .pdf, .txt
    
    - **file**: Document file to upload
    - **source_lang**: Source language code (default: zh-Hans)
    - **target_lang**: Target language code (default: en)
    - **use_cloud**: Use Azure cloud translation or local model (default: true)
    
    Returns a task_id to check status and download result
    """
    # Save uploaded file
    file_path = await save_upload_file(file)
    
    # Create task
    task_id = generate_task_id()
    tasks_storage[task_id] = {
        "task_id": task_id,
        "status": StatusEnum.PENDING,
        "progress": 0,
        "result": None,
        "error": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "file_name": file.filename
    }
    
    # Start background processing
    background_tasks.add_task(
        process_translation_task,
        task_id, file_path, source_lang, target_lang, use_cloud
    )
    
    return TaskResponse(
        task_id=task_id,
        status=StatusEnum.PENDING,
        message="Document translation task created"
    )


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_translation_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get translation task status
    
    - **task_id**: Task ID returned from /translate/document
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_storage[task_id]
    return TaskStatusResponse(**task)


@router.get("/download/{task_id}")
async def download_translated_document(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Download translated document
    
    - **task_id**: Task ID from completed translation task
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_storage[task_id]
    
    if task["status"] != StatusEnum.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"Task is not completed. Current status: {task['status']}"
        )
    
    output_file = task["result"]["output_file"]
    
    if not output_file or not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Translated file not found")
    
    import os
    filename = os.path.basename(output_file)
    
    return FileResponse(
        output_file,
        media_type="application/octet-stream",
        filename=filename
    )


@router.get("/languages", response_model=DataResponse)
async def get_supported_languages():
    """
    Get list of supported languages
    
    No authentication required
    """
    languages = {
        "zh-Hans": "Chinese Simplified",
        "zh-Hant": "Chinese Traditional",
        "en": "English",
        "ja": "Japanese",
        "ko": "Korean",
        "fr": "French",
        "de": "German",
        "es": "Spanish"
    }
    
    return DataResponse(
        code=200,
        message="Supported languages",
        data=languages
    )
