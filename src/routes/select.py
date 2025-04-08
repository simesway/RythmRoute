from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.models.GenreDisplayStrategy import StartingGenresStrategy
from src.models.graph_interaction import toggle_genre_expansion
from src.services.session_manager import get_req_session, store_session

router = APIRouter(prefix="/select", default_response_class=JSONResponse)


@router.post("/genre/{genre_id}")
async def add_genre(request: Request, genre_id: int):
  session = await get_req_session(request)
  session = toggle_genre_expansion(session, genre_id)
  await store_session(session)

@router.get("/genre/{genre_id}")
async def add_genre(request: Request, genre_id: int):
  session = await get_req_session(request)
  selection_data = session.selection

  selection_data.genres.append(genre_id)
  await store_session(session)
