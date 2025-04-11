from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from spotipy import Spotify

from src.database.db import SessionLocal
from src.models.ArtistDisplayStrategy import DefaultDisplayStrategy
from src.models.DataLoader import ArtistHandler
from src.models.clientData import GraphUpdate
from src.models.create_SessionResponse import create_SessionResponse
from src.models.SessionData import SessionData
from src.models.graph import GenreGraph
from src.routes.spotify import get_spotify_session
from src.services.session_manager import get_session, store_session

router = APIRouter(prefix="/artists", default_response_class=JSONResponse)

@router.get("/test")
async def test(session: SessionData = Depends(get_session)):
  sp_session = await get_spotify_session(session)
  spotify = Spotify(auth=sp_session.access_token)
  with SessionLocal() as db_session:
    a = ArtistHandler(db_session, spotify)
    artists = a.get_artists(3)
    return DefaultDisplayStrategy().generate({3: artists})


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

@router.get("/current_state")
async def get_current_graph(request: Request, session: SessionData = Depends(get_session)):
  #session = await get_session(request)
  response = create_SessionResponse(session)
  return response


