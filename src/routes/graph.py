from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from src.models.clientData import GraphUpdate
from src.models.create_SessionResponse import create_SessionResponse
from src.models.graph_interaction import toggle_genre_selection
from src.api.GenreMap import GenreMap
from src.models.GenreDisplayStrategy import StartingGenresStrategy
from src.models.SessionData import SessionData, GenreData
from src.services.session_manager import get_req_session, store_session

router = APIRouter(prefix="/graph", default_response_class=JSONResponse)

genre_map = GenreMap()


def add_data_to_json(json, session: SessionData):
  json["data"] = session.genres
  return json

@router.post("/update")
async def update_graph(request: GraphUpdate, session: SessionData = Depends(get_req_session)):
  action = request.action

  if action == "expand":
    s = session.genres.expanded
    s.append(request.id) if not request.id in s else s.remove(request.id)

  elif action == "select":
    s = session.genres.selected
    s.append(request.id) if not request.id in s else s.remove(request.id)

  elif action == "reset":
    session.genres.expanded = []
    session.genres.selected = []

  elif action == "collapse":
    session.genres.expanded = []


  await store_session(session)
  response = create_SessionResponse(session)
  return response

@router.get("/current_state")
async def get_current_graph(request: Request):
  session = await get_req_session(request)
  response = create_SessionResponse(session)
  return response

@router.get("/initial_graph")
async def get_initial_graph(request: Request):
  session = await get_req_session(request)
  layout = StartingGenresStrategy().to_json(session)
  json = add_data_to_json(layout, session)
  return json

@router.get("/genre/{genre_id}")
async def select_genre(request: Request, genre_id: int):
  session = await get_req_session(request)
  session = toggle_genre_selection(session, genre_id)
  await store_session(session)

  layout = StartingGenresStrategy().to_json(session)
  json = add_data_to_json(layout, session)
  return json


@router.get("/subgenres/{genre_id}")
async def get_subgenres(request: Request, genre_id: int):
  session = await get_req_session(request)
  session = toggle_genre_expansion(session, genre_id)
  await store_session(session)

  layout = StartingGenresStrategy().to_json(session)
  json = add_data_to_json(layout, session)
  return json

@router.get("/collapse_all")
async def collapse_all(request: Request):
  session = await get_req_session(request)
  session.genres.expanded = []
  await store_session(session)

  layout = StartingGenresStrategy().to_json(session)
  json = add_data_to_json(layout, session)
  return json

@router.get("/reset")
async def reset(request: Request):
  session = await get_req_session(request)
  session.genres = GenreData()
  await store_session(session)

  layout = StartingGenresStrategy().to_json(session)
  json = add_data_to_json(layout, session)
  return json


