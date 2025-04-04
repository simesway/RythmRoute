import json
from fastapi import Request
from typing import Optional

from src.services.redis_client import redis_client
from src.models.session_data import SessionData


async def store_session(session_data: SessionData):
  """Stores validated session data in Redis."""
  session_id = session_data.session_id
  session_dict = session_data.model_dump_json()  # Convert to dictionary
  await redis_client.set(session_id, session_dict)

async def get_req_session(request: Request) -> Optional[SessionData]:
  session_id = await get_session_id(request)
  if isinstance(session_id, str):
    return await get_session(session_id)
  else:
    return None

async def get_session_id(request: Request) -> str:
  """Retrieve session_id from cookies."""
  session_id = request.cookies.get("session_id")
  if not session_id:
    raise ValueError("No session_id cookie")
  return session_id

async def get_session(session_id: str) -> SessionData:
  """Retrieves and validates session data from Redis."""
  session_data = await redis_client.get(session_id)
  if session_data:
    session_dict = json.loads(session_data)
    return SessionData(**session_dict)
  else:
    raise ValueError("Session not found")


async def delete_session(session_id: str):
  """Delete session data."""
  await redis_client.delete(session_id)