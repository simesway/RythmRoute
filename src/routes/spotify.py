from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
import src.config as config
from src.services.redis_client import save_spotify_session, get_session
import time

router = APIRouter(prefix="/spotify")

def get_spotify_auth_handler():
  return SpotifyOAuth(
    client_id=config.SPOTIPY_CLIENT_ID,
    client_secret=config.SPOTIPY_CLIENT_SECRET,
    redirect_uri=config.SPOTIPY_REDIRECT_URI,
    scope=config.SPOTIPY_SCOPE,
    cache_path=None
  )

auth_manager = get_spotify_auth_handler()


async def get_spotify_session(session_id: str):
  """Retrieve the Spotify session and refresh token if expired."""
  session = await get_session(session_id)
  if not session or "spotify" not in session:
    return None

  token_info = session["spotify"]

  # Check if token expired
  if token_info["expires_at"] <= time.time():
    refresh_token = token_info["refresh_token"]
    new_token_info = auth_manager.refresh_access_token(refresh_token)

    # Update Redis with new token
    token_info.update(new_token_info)
    await save_spotify_session(session_id, token_info, expire=3600)

  return token_info


async def get_session_id(request: Request) -> str:
  """Retrieve session_id from cookies."""
  session_id = request.cookies.get("session_id")
  if not session_id:
    raise HTTPException(status_code=401, detail="Session not found. Start a new session.")
  return session_id


@router.get("/login")
async def login():
  """Redirect user to Spotify login page."""
  auth_url = auth_manager.get_authorize_url()
  return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(request: Request, code: str):
    """Handle Spotify authentication callback and store session in Redis."""
    session_id = await get_session_id(request)

    token_info = auth_manager.get_access_token(code, check_cache=False)
    if not token_info:
        raise HTTPException(status_code=400, detail="Failed to authenticate with Spotify")

    print(token_info)
    # Ensure we store the latest refresh token
    refresh_token = token_info.get("refresh_token")
    if not refresh_token:
        # If there's no refresh_token, retrieve the old one (Spotify sometimes does this)
        old_session = await get_session(session_id)
        refresh_token = old_session.get("spotify", {}).get("refresh_token")

    token_info["refresh_token"] = refresh_token  # Store it safely

    await save_spotify_session(session_id, token_info, expire=3600)

    return RedirectResponse("/")


@router.get("/current_user")
async def get_current_user(request: Request):
  """Get Spotify user profile info."""
  session_id = await get_session_id(request)
  token_info = await get_spotify_session(session_id)

  if not token_info:
    raise HTTPException(status_code=403, detail="Spotify session expired or not found. Login again.")

  sp = Spotify(auth=token_info["access_token"])
  return sp.current_user()


@router.get("/create_playlist")
async def create_playlist(request: Request, name: str, public: bool = True):
  """Create a new Spotify playlist."""
  session_id = await get_session_id(request)
  token_info = await get_spotify_session(session_id)

  if not token_info:
    raise HTTPException(status_code=403, detail="Spotify session expired or not found. Login again.")

  sp = Spotify(auth=token_info["access_token"])
  user_id = sp.current_user()["id"]
  playlist = sp.user_playlist_create(user=user_id, name=name, public=public)

  return {"message": "Playlist created", "playlist": playlist}


@router.get("/add_track")
async def add_track(request: Request, playlist_id: str, track_id: str):
  """Add a track to a Spotify playlist."""
  session_id = await get_session_id(request)
  token_info = await get_spotify_session(session_id)

  if not token_info:
    raise HTTPException(status_code=403, detail="Spotify session expired or not found. Login again.")

  sp = Spotify(auth=token_info["access_token"])
  sp.playlist_add_items(playlist_id=playlist_id, items=[track_id])

  return {"message": "Track added", "playlist_id": playlist_id, "track_id": track_id}

