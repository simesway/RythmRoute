from typing import Optional, Dict, List

from src.models.SessionData import GenreData, Artist, ArtistData, ArtistPool
from pydantic import BaseModel




class GenreRelationship(BaseModel):
  source: int
  target: int
  type: str

class Genre(BaseModel):
  id: int
  name: str
  description: str
  has_subgenre: bool
  is_selectable: bool

class Coordinate(BaseModel):
  x: float
  y: float

class ArtistMapData(BaseModel):
  pools: List[ArtistPool] = []
  state: ArtistData = ArtistData()

class GenreGraphData(BaseModel):
  genres: List[Genre]
  relationships: List[GenreRelationship]
  layout: Dict[int, Coordinate]
  state: GenreData = GenreData()

class SessionResponse(BaseModel):
  graph: Optional[GenreGraphData] = None
  artists: Optional[ArtistData] = None
