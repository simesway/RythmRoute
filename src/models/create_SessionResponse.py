from src.core.SpotifyCache import SpotifyCache
from src.models.ArtistHandler import ArtistHandler
from src.models.GenreDisplayStrategy import StartingGenresStrategy
from src.models.SessionResponse import SessionResponse, ArtistMapData, GenreGraphData, GenreData, GenreSelectionData
from src.core.session_manager import SessionData


async def create_SessionResponse(session: SessionData) -> SessionResponse:
  if not session:
    session = SessionData(id="temp")

  f = session.factory
  selected_genres = f.selected_genres()
  expanded_genres = f.expanded_genres()

  genres, relations, layout = StartingGenresStrategy().to_GenreGraphData(
    selected=set(selected_genres),
    expanded=set(expanded_genres),
    highlight=-1
  )
  genre_graph_data = GenreGraphData(relationships=relations, layout=layout)
  genre_data = GenreData(
    genres=genres,
    state=GenreSelectionData(
      selected=selected_genres,
      expanded=expanded_genres,
      highlight=-1
    )
  )

  artist_map = True
  artist_data = None
  if artist_map:
    pools = []
    for genre_id in selected_genres:
      pool = ArtistHandler().get_pool(genre_id)
      pools.append(pool)
    artist_data = ArtistMapData(pools=pools, sampled=f.sampled_artists() or {})

  user = SpotifyCache().get_current_user(session.id)

  return SessionResponse(genre_data=genre_data, graph=genre_graph_data, artists=artist_data, factory=f, user=user)