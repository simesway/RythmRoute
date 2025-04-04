from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List


class SelectionData(BaseModel):
  genres: List[int] = []

class SpotifySessionData(BaseModel):
  access_token: str
  token_type: str
  expires_in: int
  refresh_token: str
  scope: str
  expires_at: datetime

class SessionData(BaseModel):
  session_id: str
  selection: SelectionData = SelectionData()
  spotify: Optional[SpotifySessionData] = None