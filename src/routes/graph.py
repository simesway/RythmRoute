from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from src.models.clientData import GraphUpdate
from src.models.create_SessionResponse import create_SessionResponse
from src.models.GenreDisplayStrategy import StartingGenresStrategy
from src.models.SessionData import SessionData, GenreData
from src.services.session_manager import get_req_session, store_session

router = APIRouter(prefix="/graph", default_response_class=JSONResponse)




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


