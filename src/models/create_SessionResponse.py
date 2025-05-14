from src.models.ArtistHandler import ArtistHandler
from src.models.GenreDisplayStrategy import StartingGenresStrategy
from src.models.SessionResponse import SessionResponse, ArtistMapData, GenreGraphData, GenreData
from src.models.SessionData import SessionData
from src.core.spotify_client import SpotifyUserClient


async def create_SessionResponse(session: SessionData) -> SessionResponse:
  if not session:
    session = SessionData(id="temp")

  genres, relations, layout = StartingGenresStrategy().to_GenreGraphData(session)
  genre_graph_data = GenreGraphData(relationships=relations, layout=layout)
  genre_data = GenreData(genres=genres, state=session.genres)

  artist_map = True
  artist_data = None
  if artist_map:
    sp = SpotifyUserClient.get_spotify_client(session.id)


    pools = []
    for genre_id in session.genres.selected:
      pool = ArtistHandler().get_pool(genre_id)
      pools.append(pool)
    artist_data = ArtistMapData(pools=pools, sampled=session.artists.sampled or {})

  #artists = DefaultDisplayStrategy().generate(genre_artists) if genre_artists else None

  return SessionResponse(genre_data=genre_data, graph=genre_graph_data, artists=artist_data)