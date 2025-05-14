from pydantic import BaseModel
from typing import List, Dict, Optional
import json

from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

from random import random
from src.config import DB_SCRAPE_TIME_DELTA_DAYS, CACHE_OBJECT_TTL
from src.core.db import SessionLocal
from src.database.models import Genre, ArtistInGenre
from src.core.redis_client import redis_sync
from src.core.spotify_client import SpotifyClient


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


class ArtistHandler:
  # organic value
  o_min = 44
  o_max = 22648
  # bouncy value
  b_min = 10
  b_max = 1500

  def __init__(self):
    self.spotify = SpotifyClient().get_spotify_client()

  @staticmethod
  def load_pool_to_redis(pool: ArtistPool):
    redis_sync.setex(f"pool:genre:{int(pool.genre_id)}", CACHE_OBJECT_TTL, pool.model_dump_json())

  @staticmethod
  def load_pool_from_redis(genre_id) -> Optional[ArtistPool]:
    pool_data = redis_sync.get(f"pool:genre:{int(genre_id)}")
    return ArtistPool(**json.loads(pool_data)) if pool_data else None

  def get_pool(self, genre_id: int) -> ArtistPool:
    with SessionLocal() as session:
      genre = session.query(Genre).get(genre_id)
      pool = self.load_pool_from_redis(genre_id)
      if not pool:
        artists = self.get_and_update_artists(genre_id)
        pool = ArtistPool(
          genre_id=genre_id,
          artists=artists,
          name=genre.name,
          bouncyness=(genre.bouncy_value - self.b_min) / (self.b_max - self.b_min) ,
          organicness=(genre.organic_value - self.o_min) / (self.o_max - self.o_min),
        )
        self.load_pool_to_redis(pool)
        print("created Pool")
      return pool


  def fetch_artists(self, spotify_ids: List[str]) -> Dict[str, dict]:
    all_artists = []
    for i in range(0, len(spotify_ids), 50):
      batch = spotify_ids[i:i + 50]
      sp_artists = self.spotify.artists(batch)['artists']
      all_artists.extend(sp_artists)
    return {
      a["id"]: {
        "popularity": a.get("popularity", 0),
        "followers": a["followers"].get("total", 0),
        "spotify_genres": a.get("genres", [])
      }
      for a in all_artists
    }

  def get_and_update_artists(self, genre_id: int) -> List[Artist]:
    cutoff = datetime.now() - timedelta(days=int(DB_SCRAPE_TIME_DELTA_DAYS))
    with SessionLocal() as session:
      genre = (
        session.query(Genre)
        .options(joinedload(Genre.artists).joinedload(ArtistInGenre.artist))
        .filter_by(id=genre_id)
        .first()
      )

      artists_to_update = [
        link.artist.spotify_id for link in genre.artists
        if not link.artist.popularity or link.artist.modified_at < cutoff
      ]

      spotify_data = self.fetch_artists(artists_to_update)

      for link in genre.artists:
        artist = link.artist
        data = spotify_data.get(artist.spotify_id)
        if data:
          artist.popularity = data["popularity"]
          artist.followers = data["followers"]
          artist.spotify_genres = data["spotify_genres"]
          artist.modified_at = datetime.now()

      session.commit()

      artists = [
        Artist(
          id=l.artist.id,
          spotify_id=l.artist.spotify_id,
          name=l.artist.name,
          bouncyness=l.bouncy_value,
          organicness=l.organic_value,
          popularity=l.artist.popularity or 0
        ) for l in genre.artists
      ]
    return self.normalize_coordinates(artists)

  @staticmethod
  def normalize_coordinates(artists: List[Artist]) -> List[Artist]:
    bouncy_vals = [artist.bouncyness for artist in artists if artist.bouncyness]
    organic_vals = [artist.organicness for artist in artists if artist.organicness]
    b_min, b_max = min(bouncy_vals), max(bouncy_vals)
    o_min, o_max = min(organic_vals), max(organic_vals)

    for a in artists:

      a.bouncyness = (a.bouncyness - b_min) / (b_max - b_min) if a.bouncyness else random()
      a.organicness = (a.organicness - o_min) / (o_max - o_min) if a.organicness else random()

    return artists

  @classmethod
  def initialize(cls):
    with SessionLocal() as session:
      genres = session.query(Genre).filter(Genre.bouncy_value.isnot(None)).all()

      bouncy_vals = [genre.bouncy_value for genre in genres if genre.bouncy_value]
      organic_vals = [genre.organic_value for genre in genres if genre.organic_value]
      cls.b_min, cls.b_max = min(bouncy_vals), max(bouncy_vals)
      cls.o_min, cls.o_max = min(organic_vals), max(organic_vals)


ArtistHandler.initialize()