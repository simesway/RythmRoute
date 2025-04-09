from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List



class GenreData(BaseModel):
  selected: List[int] = []
  expanded: List[int] = []

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