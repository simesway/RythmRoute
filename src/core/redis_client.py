import redis

redis_client = redis.asyncio.from_url("redis://localhost:6379", decode_responses=True)
redis_sync = redis.Redis(host="localhost", port=6379, decode_responses=True)