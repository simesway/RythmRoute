from spotipy import Spotify

from src.database.db import SessionLocal
from src.models.ArtistDisplayStrategy import DefaultDisplayStrategy
from src.models.DataLoader import ArtistHandler
from src.models.GenreDisplayStrategy import StartingGenresStrategy
from src.models.SessionResponse import SessionResponse, ArtistMapData
from src.models.SessionData import SessionData
from src.routes.spotify import get_spotify_session


async def create_SessionResponse(session: SessionData) -> SessionResponse:
  if not session:
    session = SessionData(id="temp")

  genre_graph_data = StartingGenresStrategy().to_GenreGraphData(session)
  genre_graph_data.state = session.genres


  sp_session = await get_spotify_session(session)
  spotify = Spotify(auth=sp_session.access_token)


  genre_artists = {}
  for genre_id in session.genres.selected:
    with SessionLocal() as db_session:
      a = ArtistHandler(db_session, spotify)
      artists_objs = a.get_artists(genre_id)
    genre_artists[genre_id] = artists_objs
  artists = DefaultDisplayStrategy().generate(genre_artists) if genre_artists else None

  return SessionResponse(graph=genre_graph_data, artists=artists)