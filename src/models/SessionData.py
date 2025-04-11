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
  followers: int
  genres: List[str]
  images: List[ImageObject]

class ArtistData(BaseModel):
  selected: List[str] = []

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
  spotify: Optional[SpotifySessionData] = None