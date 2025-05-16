from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from src.models.PlaylistEditor import PlaylistEditor
from src.models.SessionData import SessionData
from src.models.SongSampler import TopSongsConfig

from src.core.session_manager import get_session, store_session
from src.core.spotify_client import SpotifyUserClient

router = APIRouter(prefix="/playlist", default_response_class=JSONResponse)

@router.post("/create")
async def create_playlist(request: Request, session: SessionData = Depends(get_session)):
  sp = SpotifyUserClient.get_spotify_client(session.id)
  data = await request.json()

  if data["name"] == "":
    return {}

  print(session.playlist)
  if not session.playlist:
    playlist = PlaylistEditor(name=data["name"])
    playlist.set_spotify_client(sp)
    playlist.create()
    session.playlist = playlist
    await store_session(session)
  else:
    playlist = session.playlist
    playlist.set_spotify_client(sp)

  for g_id in session.factory.selected_genres():
    session.factory.sample_tracks(g_id, TopSongsConfig(), limit=data["length"])
  tracks = session.factory.sampled_tracks()

  playlist.add_tracks(list(tracks))

  session.playlist = playlist
  await store_session(session)

  return playlist.to_frontend()

@router.get("/current")
async def get_current_playlist(session: SessionData = Depends(get_session)):
  return session.playlist.to_frontend() if session.playlist else None



