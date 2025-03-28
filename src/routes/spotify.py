from fastapi import APIRouter, Request, HTTPException
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import src.config as config
router = APIRouter(prefix="/spotify")

def get_spotify_auth_handler():
  return SpotifyOAuth(
    client_id=config.SPOTIPY_CLIENT_ID,
    client_secret=config.SPOTIPY_CLIENT_SECRET,
    redirect_uri=config.SPOTIPY_REDIRECT_URI,
    scope=config.SPOTIPY_SCOPE
  )

sp_oauth = get_spotify_auth_handler()

@router.get("/login_spotify")
async def login_spotify():
  return {"auth_url": sp_oauth.get_authorize_url()}


@router.get("/callback")
async def spotify_callback(request: Request, code: str):
  token_info = sp_oauth.get_access_token(code)

  if not token_info:
    raise HTTPException(status_code=400, detail="Spotify authentication failed")

  request.session["spotify_token"] = token_info
  return {"message": "Spotify authentication successful"}


@router.get("/me")
async def get_spotify_user(request: Request):
  token_info = request.session.get("spotify_token")

  if not token_info:
    raise HTTPException(status_code=401, detail="Not authenticated with Spotify")

  sp = spotipy.Spotify(auth=token_info["access_token"])
  return {"user": sp.current_user()}


@router.get("/playlists")
async def get_playlists(request: Request):
  token_info = request.session.get("spotify_token")

  if not token_info:
    raise HTTPException(status_code=401, detail="Not authenticated with Spotify")

  sp = spotipy.Spotify(auth=token_info["access_token"])
  return {"playlists": sp.current_user_playlists()}
