from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from src.models.DataLoader import ArtistHandler
from src.models.PlaylistEditor import PlaylistEditor
from src.models.SessionData import SessionData
from src.models.SongSampler import SongSampler

from src.services.session_manager import get_session, store_session
from src.services.spotify_client import SpotifyUserClient

router = APIRouter(prefix="/playlist", default_response_class=JSONResponse)

def sample_songs(session: SessionData):
  print(session.genres.selected)

  sampled_songs = {}
  for g in session.genres.selected:
    pool = ArtistHandler().get_pool(g)
    sampled = session.artists.sampled[g]
    artist_ids = [a.spotify_id for a in pool.artists if a.id in sampled]
    songs = SongSampler().sample_songs(artist_ids, 2)
    sampled_songs[g] = songs


  return sampled_songs

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

  genre_songs = sample_songs(session)
  tracks = [song for genre, songs in genre_songs.items() for song in songs]

  playlist.add_tracks(tracks)

  session.playlist = playlist
  await store_session(session)

  return playlist.to_frontend()

@router.get("/current")
async def get_current_playlist(session: SessionData = Depends(get_session)):
  return session.playlist.to_frontend() if session.playlist else {}



