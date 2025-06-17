from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.models.clientData import GraphUpdate
from src.models.create_SessionResponse import create_SessionResponse
from src.core.GenreGraph import GenreGraph
from src.core.session_manager import get_session, store_session, SessionData

router = APIRouter(prefix="/graph", default_response_class=JSONResponse)



@router.post("/update")
async def update_graph(request: GraphUpdate, session: SessionData = Depends(get_session)):
  action = request.action
  f = session.factory

  if request.name is not None and request.id is None:
    request.id = GenreGraph().get_genre_id(request.name)

  genre_id = request.id

  if genre_id is None:
    raise ValueError("Genre ID must be provided.")

  if action == "expand":
    if genre_id not in f.genres:
      f.add_genre(genre_id)

    f.toggle_expand(genre_id)

  elif action == "highlight":
    pass

  elif action == "select":
    if genre_id not in f.genres:
      f.add_genre(genre_id)
    f.toggle_select(request.id)

  elif action == "reset":
    f.clear()

  elif action == "collapse":
    f.collapse_all()

  f.remove_unexplored()

  await store_session(session)
  response = await create_SessionResponse(session)
  return response

@router.get("/current_state")
async def get_current_graph(session: SessionData = Depends(get_session)):
  response = await create_SessionResponse(session)
  return response


