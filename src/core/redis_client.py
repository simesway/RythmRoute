import redis
from src.config import REDIS_HOST, REDIS_PORT

redis_client = redis.asyncio.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True)
redis_sync = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)