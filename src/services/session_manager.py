import json
from fastapi import Request, Response
from starlette.responses import RedirectResponse
from typing import Optional

from src.config import SESSION_EXPIRE_TIME
from src.services.redis_client import redis_client
from src.models.SessionData import SessionData


async def store_session(session_data: SessionData):
  """Stores validated session data in Redis."""
  session_id = session_data.id
  session_dict = session_data.model_dump_json()  # Convert to dictionary
  await redis_client.setex(session_id, SESSION_EXPIRE_TIME, session_dict)

async def get_req_session(request: Request) -> Optional[SessionData]:
  session_id = await get_session_id(request)
  if isinstance(session_id, str):
    return await get_session(session_id)
  else:
    return None

async def get_session_id(request: Request) -> Optional[str]:
  """Retrieve session_id from cookies."""
  session_id = request.cookies.get("session_id")
  if not session_id:
    return None
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