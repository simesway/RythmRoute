from dataclasses import field
from pydantic import BaseModel
from typing import Optional, Dict, List

from src.core.SpotifyCache import SpotifyUser
from src.models.ArtistHandler import ArtistPool
from src.models.PlaylistFactory import PlaylistFactory


class GenreRelationship(BaseModel):
  source: int
  target: int
  type: str

class Genre(BaseModel):
  id: int
  name: str
  bouncyness: Optional[float] = None
  organicness: Optional[float] = None
  has_subgenre: bool
  is_selectable: bool

class GenreSelectionData(BaseModel):
  selected: List[int] = []
  expanded: List[int] = []
  highlight: Optional[int] = None

class GenreData(BaseModel):
  genres: List[Genre] = []
  state: GenreSelectionData = GenreSelectionData()

class Coordinate(BaseModel):
  x: float
  y: float

class ArtistMapData(BaseModel):
  pools: List[ArtistPool] = []
  sampled: Dict[int, list] = field(default_factory=dict)

class GenreGraphData(BaseModel):
  relationships: List[GenreRelationship]
  layout: Dict[int, Coordinate]

class SessionResponse(BaseModel):
  genre_data: GenreData = GenreData()
  graph: Optional[GenreGraphData] = None
  artists: Optional[ArtistMapData] = None
  factory: Optional[PlaylistFactory] = None
  user: Optional[SpotifyUser] = None
