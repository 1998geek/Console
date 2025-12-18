import uuid
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from app.db.redis_client import redis_conn
import json

logger = logging.getLogger(__name__)

class TaskManager:
    """
    Manages asynchronous background tasks.
    Uses Redis to store task status and results.
    """
    
    @staticmethod
    def init_task(task_type: str, metadata: Dict[str, Any] = None) -> str:
        """Initialize a new task and return its ID."""
        task_id = str(uuid.uuid4())
        task_key = f"task:{task_id}"
        
        data = {
            "id": task_id,
            "type": task_type,
            "status": "pending",
            "progress": 0,
            "message": "Task initialized",
            "created_at": datetime.now().isoformat(),
            "metadata": json.dumps(metadata or {})
        }
        
        redis_conn.hset(task_key, mapping=data)
        # Set expiry to 24 hours
        redis_conn.expire(task_key, 86400)
        
        return task_id

    @staticmethod
    def update_progress(task_id: str, progress: int, message: str = None):
        """Update task progress (0-100)."""
        task_key = f"task:{task_id}"
        updates = {"progress": progress}
        if message:
            updates["message"] = message
        
        # Only update if task exists
        if redis_conn.exists(task_key):
            redis_conn.hset(task_key, mapping=updates)

    @staticmethod
    def complete_task(task_id: str, result: Any):
        """Mark task as completed and store result."""
        task_key = f"task:{task_id}"
        updates = {
            "status": "completed",
            "progress": 100,
            "message": "Task completed successfully",
            "result": json.dumps(result) if result else "",
            "completed_at": datetime.now().isoformat()
        }
        
        if redis_conn.exists(task_key):
            redis_conn.hset(task_key, mapping=updates)

    @staticmethod
    def fail_task(task_id: str, error: str):
        """Mark task as failed."""
        task_key = f"task:{task_id}"
        updates = {
            "status": "failed",
            "error": error,
            "message": f"Task failed: {error}",
            "failed_at": datetime.now().isoformat()
        }
        
        if redis_conn.exists(task_key):
            redis_conn.hset(task_key, mapping=updates)

    @staticmethod
    def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status."""
        task_key = f"task:{task_id}"
        data = redis_conn.hgetall(task_key)
        
        if not data:
            return None
            
        # Parse JSON fields
        if "metadata" in data:
            try:
                data["metadata"] = json.loads(data["metadata"])
            except:
                pass
        
        if "result" in data and data["result"]:
            try:
                data["result"] = json.loads(data["result"])
            except:
                pass

        if "progress" in data:
            try:
                data["progress"] = int(data["progress"])
            except:
                data["progress"] = 0
                
        return data
