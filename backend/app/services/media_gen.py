import time
import uuid
from app.db.redis_client import redis_conn

class SoraService:
    @staticmethod
    def mock_sora_generation(task_id: str, prompt: str):
        redis_conn.hset(f"task:{task_id}", mapping={"status": "processing"})
        time.sleep(10)
        result_url = "https://www.w3schools.com/html/mov_bbb.mp4"
        redis_conn.hset(f"task:{task_id}", mapping={"status": "completed", "result": result_url})

    @staticmethod
    def init_task(prompt: str) -> str:
        task_id = str(uuid.uuid4())
        redis_conn.hset(f"task:{task_id}", mapping={"status": "pending", "prompt": prompt})
        return task_id
