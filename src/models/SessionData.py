from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List


class ImageObject(BaseModel):
  url: str
  height: int
  width: int


class Album(BaseModel):
  spotify_id: str
  name: str
  album_type: str
  total_tracks: int
  release_date: datetime
  images: List[ImageObject]
  artists: List[str] = []


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
  selected: List[int] = []

class GenreData(BaseModel):
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

class SessionData(BaseModel):
  id: str
  genres: GenreData = GenreData()
  artists: ArtistData = ArtistData()
  spotify: Optional[SpotifySessionData] = None