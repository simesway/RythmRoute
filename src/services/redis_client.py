import redis.asyncio as redis
import json

redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

async def save_session(session_id: str, data: dict, expire: int):
    """Save session data to Redis."""
    await redis_client.set(session_id, json.dumps(data), ex=expire)

async def get_session(session_id: str):
    """Retrieve the full session (including Spotify data)."""
    session_data = await redis_client.get(session_id)
    return json.loads(session_data) if session_data else {}

async def delete_session(session_id: str):
    """Delete session data."""
    await redis_client.delete(session_id)


async def save_spotify_session(session_id: str, token_info: dict, expire: int = 3600):
    """Merge Spotify session into the existing Redis session."""
    session_data = await redis_client.get(session_id)
    session = json.loads(session_data) if session_data else {}

    # Add/Update Spotify session data
    session["spotify"] = token_info

    await redis_client.set(session_id, json.dumps(session), ex=expire)
