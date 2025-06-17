from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from src.models.PlaylistEditor import PlaylistEditor
from src.core.session_manager import get_session, store_session, SessionData
from src.core.spotify_client import SpotifyUserClient

router = APIRouter(prefix="/playlist", default_response_class=JSONResponse)

@router.post("/create")
async def create_playlist(request: Request, session: SessionData = Depends(get_session)):
  sp = SpotifyUserClient(session.id).get_spotify_client()
  data = await request.json()

  if data["name"] == "":
    return {}

  factory = session.factory
  if not isinstance(factory.playlist, PlaylistEditor) or factory.playlist.id is None:
    factory.create_playlist(sp, data["name"])

  factory.playlist.set_spotify(sp)
  factory.update_playlist()

  await store_session(session)

  return factory.playlist.to_frontend()


@router.get("/update")
async def update_playlist(session: SessionData = Depends(get_session)):
  sp = SpotifyUserClient(session.id).get_spotify_client()
  factory = session.factory
  factory.playlist.set_spotify(sp)
  factory.update_playlist()
  await store_session(session)
  return factory.playlist.to_frontend()

@router.get("/current")
async def get_current_playlist(session: SessionData = Depends(get_session)):
  return session.factory.playlist.to_frontend() if session.factory.playlist else None



