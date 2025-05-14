from fastapi import APIRouter, Request, HTTPException, Response, Depends
import uuid
from src.config import SESSION_USER_EXPIRE_TIME, SESSION_COOKIE_NAME
from src.models.SessionData import SessionData
from src.core.session_manager import store_session, get_session, delete_session

router = APIRouter(prefix="/session")


async def get_session_id(request: Request) -> str:
  """Retrieve session_id from cookies."""
  session_id = request.cookies.get("session_id")
  if not session_id:
    raise HTTPException(status_code=401, detail="Session not found. Start a new session.")
  return session_id

@router.get("/start")
async def start_session(response: Response):
  """Create a new session and store it in a cookie."""
  session_id = str(uuid.uuid4())
  await store_session(SessionData(id=session_id))

  response.set_cookie(
    key="session_id",
    value=session_id,
    httponly=True,
    max_age=SESSION_USER_EXPIRE_TIME,
    secure=True,  # Use secure cookies (HTTPS only)
    samesite="Lax"  # Helps prevent CSRF attacks
  )
  return {"message": "Session started", "session_id": session_id}


@router.get("/status")
async def session_status(request: Request, session: SessionData = Depends(get_session)):
  """Check if a session exists and return its data."""

  if not session:
    raise HTTPException(status_code=404, detail="Session expired or not found")

  return session


@router.get("/stop")
async def stop_session(request: Request, response: Response):
  """Delete the session and remove the cookie."""
  session_id = await get_session_id(request)
  await delete_session(session_id)

  response.delete_cookie("session_id")  # Remove cookie from client
  return {"message": "Session stopped and cookie cleared"}