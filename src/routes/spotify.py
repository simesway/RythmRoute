from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from src.core.session_manager import get_session, SessionData

from src.core.spotify_client import SpotifyUserClient

router = APIRouter(prefix="/spotify")


@router.get("/login")
async def login(session: SessionData = Depends(get_session)):
  """Redirect user to Spotify login page."""
  return RedirectResponse(SpotifyUserClient(session.id).get_auth_url())

@router.get("/callback")
async def callback(code: str, session: SessionData = Depends(get_session)):
  """Handle Spotify authentication callback and store session in Redis."""
  SpotifyUserClient(session.id).fetch_and_store_token(code)
  return RedirectResponse("/")


@router.get("/current_user")
async def get_current_user(session: SessionData = Depends(get_session)):
  """Get Spotify user profile info."""
  sp = SpotifyUserClient(session.id).get_spotify_client()
  return sp.current_user()


