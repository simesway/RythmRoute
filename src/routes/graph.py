from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.models.graph_interaction import toggle_genre_selection
from src.api.GenreMap import GenreMap
from src.models.GenreDisplayStrategy import StartingGenresStrategy
from src.models.graph_interaction import toggle_genre_expansion
from src.models.session_data import SessionData, GenreData
from src.services.session_manager import get_req_session, store_session

router = APIRouter(prefix="/graph", default_response_class=JSONResponse)

genre_map = GenreMap()


def add_data_to_json(json, session: SessionData):
  json["data"] = session.genres
  return json


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


