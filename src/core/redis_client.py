import redis
from src.config import RedisConfig

redis_client = redis.asyncio.from_url(f"redis://{RedisConfig.host}:{RedisConfig.port}", decode_responses=True)
redis_sync = redis.Redis(host=RedisConfig.host, port=RedisConfig.port, decode_responses=True)