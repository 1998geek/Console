from fastapi import APIRouter, HTTPException, Depends
from app.services.tasks.task_manager import TaskManager
from app.api import deps

router = APIRouter()

@router.get("/{task_id}")
async def get_task_status(task_id: str, current_user = Depends(deps.get_current_user)):
    """
    Get the status of a background task.
    """
    status = TaskManager.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status
