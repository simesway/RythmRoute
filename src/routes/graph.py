from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.models.clientData import GraphUpdate
from src.models.create_SessionResponse import create_SessionResponse
from src.models.SessionData import SessionData
from src.core.GenreGraph import GenreGraph
from src.core.session_manager import get_session, store_session

router = APIRouter(prefix="/graph", default_response_class=JSONResponse)



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
    s.append(request.id) if not request.id in s else s.remove(request.id)
    session.genres.highlight = request.id

  elif action == "reset":
    session.genres.expanded = []
    session.genres.selected = []
    session.genres.highlight = None

  elif action == "collapse":
    session.genres.expanded = []
    session.genres.highlight = None


  await store_session(session)
  response = await create_SessionResponse(session)
  return response

@router.get("/current_state")
async def get_current_graph(session: SessionData = Depends(get_session)):
  response = await create_SessionResponse(session)
  return response


