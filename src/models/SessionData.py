from dataclasses import field

from datetime import datetime

from pydantic import BaseModel
from spotipy import Spotify
from typing import Optional, List, Dict

from src.models.ArtistHandler import ArtistPool
from src.models.PlaylistEditor import PlaylistEditor


class ArtistData(BaseModel):
  pools: List[ArtistPool] = []
  sampled: Dict[int, list] = field(default_factory=dict)

class GenreSelectionData(BaseModel):
  selected: List[int] = []
  expanded: List[int] = []
  highlight: Optional[int] = None

class SpotifySessionData(BaseModel):
  access_token: str
  token_type: str
  expires_in: int
  refresh_token: str
  scope: str
  expires_at: datetime

  def __call__(self):
    return Spotify(auth=self.access_token)


class SessionData(BaseModel):
  id: str
  genres: GenreSelectionData = GenreSelectionData()
  artists: ArtistData = ArtistData()
  spotify: Optional[SpotifySessionData] = None
  playlist: Optional[PlaylistEditor] = None