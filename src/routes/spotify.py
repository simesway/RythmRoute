from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from typing import Union
import src.config as config
from src.models.SessionData import SpotifySessionData, SessionData
from src.services.session_manager import store_session, get_session, get_session_id, get_session, get_session_from_id
from datetime import datetime, timezone

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


async def get_spotify_session(session: SessionData) -> Union[RedirectResponse, SpotifySessionData]:
  """Retrieve the Spotify session and refresh token if expired."""
  spotify_session = session.spotify

  if not spotify_session:
    return RedirectResponse("/spotify/login")

  # Check if token expired
  if spotify_session.expires_at <= datetime.now(timezone.utc):
    refresh_token = spotify_session.refresh_token
    token_info = auth_manager.refresh_access_token(refresh_token)

    spotify_session = SpotifySessionData(
      access_token=token_info["access_token"],
      refresh_token=token_info["refresh_token"],
      expires_in=token_info["expires_in"],
      expires_at=token_info["expires_at"],
      token_type=token_info["token_type"],
      scope=token_info["scope"]
    )
    await save_spotify_session(session.id, spotify_session)

  return spotify_session


async def save_spotify_session(session_id: str, spotify_session: SpotifySessionData):
  """Merge Spotify session into the existing Redis session."""
  session = await get_session_from_id(session_id)
  session.spotify = spotify_session
  await store_session(session)


@router.get("/login")
async def login():
  """Redirect user to Spotify login page."""
  auth_url = auth_manager.get_authorize_url()
  return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(request: Request, code: str, session: SessionData = Depends(get_session)):
  """Handle Spotify authentication callback and store session in Redis."""

  token_info = auth_manager.get_access_token(code, check_cache=False)
  if not token_info:
    raise HTTPException(status_code=400, detail="Failed to authenticate with Spotify")


  # Ensure we store the latest refresh token
  refresh_token = token_info.get("refresh_token")
  if not refresh_token:
    # If there's no refresh_token, retrieve the old one (Spotify sometimes does this)
    refresh_token = session.get("spotify", {}).get("refresh_token")

  spotify_session = SpotifySessionData(
    access_token=token_info["access_token"],
    refresh_token=refresh_token,
    expires_in=token_info["expires_in"],
    expires_at=token_info["expires_at"],
    token_type=token_info["token_type"],
    scope=token_info["scope"]
  )

  await save_spotify_session(session.id, spotify_session)

  return RedirectResponse("/")


@router.get("/current_user")
async def get_current_user(request: Request, session: SessionData = Depends(get_session)):
  """Get Spotify user profile info."""
  sp_session = await get_spotify_session(session)

  if not sp_session:
    raise HTTPException(status_code=403, detail="Spotify session expired or not found. Login again.")

  sp = Spotify(auth=sp_session.access_token)
  return sp.current_user()


@router.get("/create_playlist")
async def create_playlist(request: Request, name: str, public: bool = True):
  """Create a new Spotify playlist."""
  session = await get_session(request)
  sp_session = await get_spotify_session(session)

  if not sp_session:
    raise HTTPException(status_code=403, detail="Spotify session expired or not found. Login again.")

  sp = Spotify(auth=sp_session.access_token)
  user_id = sp.current_user()["id"]
  playlist = sp.user_playlist_create(user=user_id, name=name, public=public)

  return {"message": "Playlist created", "playlist": playlist}


@router.get("/add_track")
async def add_track(request: Request, playlist_id: str, track_id: str):
  """Add a track to a Spotify playlist."""
  session = await get_session(request)
  sp_session = await get_spotify_session(session)

  if not sp_session:
    raise HTTPException(status_code=403, detail="Spotify session expired or not found. Login again.")

  sp = Spotify(auth=sp_session.access_token)
  sp.playlist_add_items(playlist_id=playlist_id, items=[track_id])

  return {"message": "Track added", "playlist_id": playlist_id, "track_id": track_id}

