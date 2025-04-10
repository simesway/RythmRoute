from typing import Optional, Dict, List

from src.models.SessionData import GenreData
from pydantic import BaseModel


class GenreState(BaseModel):
  selected: List[int] = []
  expanded: List[int] = []
  highlight: Optional[int] = None

class GenreRelationship(BaseModel):
  source: int
  target: int
  type: str

class Genre(BaseModel):
  id: int
  name: str
  description: str
  has_subgenre: bool

class Coordinate(BaseModel):
  x: float
  y: float

class GenreGraphData(BaseModel):
  genres: List[Genre]
  relationships: List[GenreRelationship]
  layout: Dict[int, Coordinate]
  state: GenreData = GenreData()

class SessionResponse(BaseModel):
  graph: Optional[GenreGraphData]
