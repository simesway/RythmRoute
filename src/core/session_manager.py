import uuid
import json
import logging
from json import JSONDecodeError
from fastapi import Request, Response
from pydantic import BaseModel, Field
from typing import Optional

from src.config import SESSION_USER_EXPIRE_TIME, SESSION_COOKIE_NAME
from src.core.redis_client import redis_client
from src.models.PlaylistEditor import PlaylistEditor
from src.models.PlaylistFactory import PlaylistFactory

logger = logging.getLogger("SessionManager")
logger.setLevel(logging.DEBUG)


COOKIE_PARAMS = dict(
    key=SESSION_COOKIE_NAME,
    httponly=True,
    secure=True,
    samesite="Lax",
    max_age=SESSION_USER_EXPIRE_TIME,
)


class SessionData(BaseModel):
  id: str
  factory: PlaylistFactory = Field(default_factory=PlaylistFactory)
  playlist: Optional[PlaylistEditor] = None


async def refresh_ttl_and_cookie(session_id: str, response: Response):
  logger.debug(f"Refreshed session TTL and cookie: {session_id}")
  await redis_client.expire(session_id, SESSION_USER_EXPIRE_TIME)
  response.set_cookie(value= session_id, **COOKIE_PARAMS)

async def create_session(response: Response) -> SessionData:
  """Create a new session with a fresh UUID, store it in Redis, and set cookie."""
  session_id = str(uuid.uuid4())
  session_data = SessionData(id=session_id)
  await store_session(session_data)
  await refresh_ttl_and_cookie(session_id, response)
  logger.info(f"Created session {session_id}")
  return session_data


async def create_session_once(session_id: str) -> SessionData:
  """
  Create a session with the given ID only if it does not already exist in Redis.
  If the session exists, load and return the existing one.
  """
  session_data = SessionData(id=session_id)
  session_json = session_data.model_dump_json()
  was_set = await redis_client.setnx(session_id, session_json)
  if was_set:
    await redis_client.expire(session_id, SESSION_USER_EXPIRE_TIME)
    logger.info(f"Created new session: {session_id}")
    return session_data
  else:
    # Session exists: load and return existing
    existing = await redis_client.get(session_id)
    if existing:
      session_json = json.loads(existing)
      logger.debug(f"Session {session_id} already exists, loaded from redis.")
      return SessionData(**session_json)
    else:
      # Edge case: key disappeared after setnx failed -> create new session recursively
      logger.warning(f"Race condition detected, retrying session creation for {session_id}")
      return await create_session_once(str(uuid.uuid4()))

async def store_session(session_data: SessionData):
  """Stores validated session data in Redis."""
  session_id = session_data.id
  session_json = session_data.model_dump_json()  # Convert to dictionary
  await redis_client.setex(session_id, SESSION_USER_EXPIRE_TIME, session_json)
  logger.debug(f"Stored session in redis: {session_id}")


async def get_session(request: Request, response: Response) -> SessionData:
  """
  Retrieve or create a session based on the session_id cookie.
    Refreshes TTL if session exists, or creates a new one if missing or invalid.
    Sets or refreshes the session cookie.
  """
  session_id = request.cookies.get(COOKIE_PARAMS["key"])
  if not session_id:
    session_id = str(uuid.uuid4())
    session_data = await create_session_once(session_id)
    await refresh_ttl_and_cookie(session_id, response)
    logger.info("No session_id cookie found. Created new session.")
    return session_data

  try:
    session_data = await get_session_from_id(session_id)
  except (ValueError, JSONDecodeError) as e:
    response.delete_cookie(COOKIE_PARAMS["key"])
    session_id = str(uuid.uuid4()) # new session id
    session_data = await create_session_once(session_id)
    logger.info(f"Session invalid, created new session: {session_id} {e}")

  await refresh_ttl_and_cookie(session_id, response)
  return session_data

async def get_session_id(request: Request) -> Optional[str]:
  """Retrieve session_id from cookies."""
  session_id = request.cookies.get(COOKIE_PARAMS["key"])
  logger.debug(f"Retrieved session_id from cookie: {session_id}")
  return session_id

async def get_session_from_id(session_id: str) -> SessionData:
  """Retrieves and validates session data from Redis."""
  session_data = await redis_client.get(session_id)
  if session_data:
    session_dict = json.loads(session_data)
    logger.debug(f"Loaded session from redis: {session_id}")
    return SessionData(**session_dict)
  else:
    logger.debug(f"Session not found in redis: {session_id}")
    raise ValueError("Session not found")


async def delete_session(session_id: str):
  """Delete session data."""
  await redis_client.delete(session_id)
  logger.info(f"Deleted session: {session_id}")