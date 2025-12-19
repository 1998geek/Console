import redis
from app.core.config import settings
import json

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True # 自动解码为字符串
        )

    def set_task_progress(self, task_id: str, progress: int, message: str, status: str = "processing", download_url: str = None):
        """
        更新任务进度到 Redis
        Key格式: task:{task_id}
        """
        data = {
            "progress": progress,
            "message": message,
            "status": status,
            "download_url": download_url
        }
        # 设置过期时间为 24 小时，避免 Redis 爆满
        self.client.setex(f"task:{task_id}", 86400, json.dumps(data))

    def get_task_progress(self, task_id: str):
        """获取任务进度"""
        data = self.client.get(f"task:{task_id}")
        if data:
            return json.loads(data)
        return None

# 单例对象
redis_client = RedisClient()
