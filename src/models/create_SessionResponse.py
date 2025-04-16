from spotipy import Spotify

from src.database.db import SessionLocal
from src.models.ArtistDisplayStrategy import AllPoolsDisplayStrategy
from src.models.DataLoader import ArtistHandler
from src.models.GenreDisplayStrategy import StartingGenresStrategy
from src.models.SessionResponse import SessionResponse, ArtistMapData, GenreGraphData, GenreData
from src.models.SessionData import SessionData, ArtistPool, ArtistData
from src.routes.spotify import get_spotify_session
from src.services.session_manager import store_session


async def create_SessionResponse(session: SessionData) -> SessionResponse:
  if not session:
    session = SessionData(id="temp")

  genres, relations, layout = StartingGenresStrategy().to_GenreGraphData(session)
  genre_graph_data = GenreGraphData(relationships=relations, layout=layout)
  genre_data = GenreData(genres=genres, state=session.genres)

  sp_session = await get_spotify_session(session)
  spotify = Spotify(auth=sp_session.access_token)


  pools = []
  for genre_id in session.genres.selected:
    pool = ArtistHandler(sp_session=spotify).get_pool(genre_id)
    pools.append(pool)
  artist_data = ArtistData(pools=pools)

  #artists = DefaultDisplayStrategy().generate(genre_artists) if genre_artists else None

  return SessionResponse(genre_data=genre_data, graph=genre_graph_data, artists=artist_data)