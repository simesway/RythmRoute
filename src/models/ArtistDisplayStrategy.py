from abc import ABC, abstractmethod
from typing import List, Dict

from random import random
from src.models.SessionData import SessionData, Artist, ArtistData
from src.models.SessionResponse import ArtistMapData, Coordinate
from src.models.graph import GenreGraph


class PoolDisplayStrategy(ABC):
  @abstractmethod
  def generate(self, data: ArtistData) -> ArtistMapData:
    """Must be implemented by subclasses."""
    pass


class AllPoolsDisplayStrategy(PoolDisplayStrategy):
  @staticmethod
  def normalize_layout(layout: Dict[str, Coordinate]) -> Dict[str, Coordinate]:
    x = [p.x for p in layout.values()]
    y = [p.y for p in layout.values()]

    x_min, x_max = min(x), max(x)
    y_min, y_max = min(y), max(y)

    for coordinate in layout.values():
      coordinate.x = (coordinate.x - x_min) / (x_max - x_min)
      coordinate.y = (coordinate.y - y_min) / (y_max - y_min)

    return layout

  def generate(self, data: ArtistData) -> ArtistMapData:

    artists: List[Artist] = []
    for pool in data.pools:
      artists.extend(pool.artists)

