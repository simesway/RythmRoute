from src.models.GenreDisplayStrategy import StartingGenresStrategy
from src.models.SessionResponse import SessionResponse
from src.models.session_data import SessionData


def create_SessionResponse(session: SessionData) -> SessionResponse:
  if not session:
    session = SessionData(id="temp")

  genre_graph_data = StartingGenresStrategy().to_GenreGraphData(session)


  return SessionResponse(graph=genre_graph_data)