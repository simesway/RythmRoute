import redis.asyncio as redis
import json

redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
