import redis
from app.core.config import settings

redis_conn = redis.from_url(settings.REDIS_URL, decode_responses=True)
