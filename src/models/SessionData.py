from pydantic import BaseModel, Field
from typing import Optional

from src.models.PlaylistEditor import PlaylistEditor
from src.models.PlaylistFactory import PlaylistFactory


class SessionData(BaseModel):
  id: str
  factory: PlaylistFactory = Field(default_factory=PlaylistFactory)
  playlist: Optional[PlaylistEditor] = None