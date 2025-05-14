from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.models.ArtistHandler import ArtistHandler
from src.models.ObjectSampling import AttributeWeightedSampling
from src.models.clientData import GraphUpdate
from src.models.create_SessionResponse import create_SessionResponse
from src.models.SessionData import SessionData
from src.core.GenreGraph import GenreGraph
from src.core.SpotifyCache import SpotifyCache
from src.core.session_manager import get_session, store_session

router = APIRouter(prefix="/artists", default_response_class=JSONResponse)

@router.post("/sample/{genre_id}")
async def sample_artists(genre_id: int, sampler: AttributeWeightedSampling, session: SessionData = Depends(get_session)):
  pool = ArtistHandler().get_pool(genre_id)

  artists = pool.artists
  sampled = []
  for i in range(20):
    sampled.append(sampler(artists))

  sampled_ids = set(sample.id for sample in sampled)

  session.artists.sampled[genre_id] = list(sampled_ids)
  await store_session(session)
  return await create_SessionResponse(session)



@router.post("/update")
async def update_graph(request: GraphUpdate, session: SessionData = Depends(get_session)):
  action = request.action

  if action == "expand":
    s = session.genres.expanded
    if request.name is not None and request.id is None:
      request.id = GenreGraph().get_genre_id(request.name)


    if not request.id in s:
      session.genres.highlight = request.id
      s.append(request.id)
    else:
      #session.genres.highlight = None
      s.remove(request.id)

  elif action == "highlight":
    session.genres.highlight = request.id

  elif action == "select":
    s = session.genres.selected
    session.genres.highlight = request.id
    s.append(request.id) if not request.id in s else s.remove(request.id)

  elif action == "reset":
    session.genres.expanded = []
    session.genres.selected = []
    session.genres.highlight = None

  elif action == "collapse":
    session.genres.expanded = []
    session.genres.highlight = None


  await store_session(session)
  response = create_SessionResponse(session)
  return response

@router.get("/album/{artist_id}")
async def get_artist(artist_id: str):
  tracks = SpotifyCache().get_album_tracks(artist_id)
  return tracks


@router.get("/releases/{artist_id}")
async def get_releases(artist_id: str):
  return SpotifyCache().get_releases(artist_id)


@router.get("/top_tracks/{artist_id}")
async def get_releases(artist_id: str):
  return SpotifyCache().get_top_tracks(artist_id)

