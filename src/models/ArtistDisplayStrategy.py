from abc import ABC, abstractmethod
from typing import List, Dict

from random import random
from src.models.SessionData import SessionData, Artist
from src.models.SessionResponse import ArtistMapData, Coordinate
from src.models.graph import GenreGraph


class DisplayStrategy(ABC):
  @abstractmethod
  def generate(self, genre_artists: Dict[int, List[Artist]]) -> ArtistMapData:
    """Must be implemented by subclasses."""
    pass


class DefaultDisplayStrategy(DisplayStrategy):
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

  def generate(self, genre_artists: Dict[int, List[Artist]]) -> ArtistMapData:
    scale = 0.5
    all_artists = []
    layout = {}
    for genre_id, artists in genre_artists.items():
      all_artists.extend(artists)
      genre = GenreGraph().get_genre(genre_id)
      if not genre["bouncy_value"]:
        continue

      bouncy_vals = [artist.bouncyness for artist in artists if artist.bouncyness]
      organic_vals = [artist.organicness for artist in artists if artist.organicness]

      b_min, b_max = min(bouncy_vals), max(bouncy_vals)
      o_min, o_max = min(organic_vals), max(organic_vals)

      for artist in artists:
        b = (artist.bouncyness - b_min) / (b_max - b_min) if artist.bouncyness else random()
        o = (artist.organicness - o_min) / (o_max - o_min) if artist.organicness else random()

        x = genre["bouncy_value"] + (b - 0.5) * scale
        y = genre["organic_value"] + (o - 0.5) * scale

        layout[artist.spotify_id] = Coordinate(x=x, y=y)

    layout = self.normalize_layout(layout) if len(layout) > 1 else None
    return ArtistMapData(artists=all_artists, layout=self.normalize_layout(layout))
