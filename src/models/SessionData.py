from dataclasses import field

from datetime import datetime

from pydantic import BaseModel
from spotipy import Spotify
from typing import Optional, List, Dict


class Artist(BaseModel):
  id: int
  spotify_id: str
  name: str
  bouncyness: float
  organicness: float
  popularity: int

class ArtistPool(BaseModel):
  genre_id: int
  name: str
  bouncyness: float
  organicness: float
  artists: List[Artist]

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