import uuid

import json
from fastapi import Request, Response
from typing import Optional

from src.config import SESSION_EXPIRE_TIME
from src.services.redis_client import redis_client
from src.models.SessionData import SessionData


def set_session_cookie(session_id: str, response: Response):
  response.set_cookie(
    key="session_id",
    value=session_id,
    max_age=SESSION_EXPIRE_TIME,
    httponly=True,
    secure=True,
    samesite="Lax"
  )

async def create_session(response: Response) -> SessionData:
  session_id = str(uuid.uuid4())
  session_data = SessionData(id=session_id)
  await store_session(session_data)
  set_session_cookie(session_id, response)
  return session_data



async def store_session(session_data: SessionData):
  """Stores validated session data in Redis."""
  session_id = session_data.id
  session_dict = session_data.model_dump_json()  # Convert to dictionary
  await redis_client.setex(session_id, SESSION_EXPIRE_TIME, session_dict)

async def get_session(request: Request, response: Response) -> SessionData:
  session_id = request.cookies.get("session_id")
  if not session_id:
    return await create_session(response)

  try:
    session_data = await get_session_from_id(session_id)

    await store_session(session_data)
    set_session_cookie(session_id, response)
    return session_data
  except ValueError:
    return await create_session(response)

async def get_session_id(request: Request) -> Optional[str]:
  """Retrieve session_id from cookies."""
  session_id = request.cookies.get("session_id")
  if not session_id:
    return None
  return session_id

async def get_session_from_id(session_id: str) -> SessionData:
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