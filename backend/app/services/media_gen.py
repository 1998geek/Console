import time
import uuid
from app.db.redis_client import redis_conn

class SoraService:
    @staticmethod
    def mock_sora_generation(task_id: str, prompt: str, width: int, height: int, duration: int):
        redis_conn.hset(
            f"task:{task_id}",
            mapping={
                "status": "processing",
                "prompt": prompt,
                "width": str(width),
                "height": str(height),
                "duration": str(duration),
            },
        )
        time.sleep(10)
        result_url = "https://www.w3schools.com/html/mov_bbb.mp4"
        redis_conn.hset(f"task:{task_id}", mapping={"status": "succeeded", "result": result_url})

    @staticmethod
    def init_task(prompt: str, width: int, height: int, duration: int) -> str:
        task_id = str(uuid.uuid4())
        redis_conn.hset(
            f"task:{task_id}",
            mapping={
                "status": "pending",
                "prompt": prompt,
                "width": str(width),
                "height": str(height),
                "duration": str(duration),
            },
        )
        return task_id
