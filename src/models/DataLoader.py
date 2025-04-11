from typing import List
from spotipy import Spotify

from sqlalchemy import select
from sqlalchemy.orm import joinedload

import src.database.models as db
from src.database.db import SessionLocal
from src.models.SessionData import Artist, SessionData, SpotifySessionData, ImageObject
from src.routes.spotify import get_spotify_session


class ArtistHandler:
  def __init__(self, db_session: SessionLocal, sp_session: Spotify):
    self.db_session = db_session
    self.spotify = sp_session

  def get_artist(self, artist: db.Artist) -> Artist:
    pass

  def get_genre_artists(self, genre_id: int) -> dict:
    stmt = (
      select(db.Genre)
      .where(db.Genre.id == genre_id)
      .options(joinedload(db.Genre.artists).joinedload(db.ArtistInGenre.artist))
    )
    genre = self.db_session.execute(stmt).unique().scalar_one()
    return {
      rel.artist.spotify_id:
        {"artist": rel.artist,
         "bouncy_value": rel.bouncy_value,
         "organic_value": rel.organic_value}
      for rel in genre.artists
    }

  def get_spotify_artists(self, artist_ids: List[str]) -> List[dict]:
    all_artists = []
    for i in range(0, len(artist_ids), 50):
      batch = artist_ids[i:i + 50]
      sp_artists = self.spotify.artists(batch)['artists']
      all_artists.extend(sp_artists)
    return all_artists

  def get_artists(self, genre_id: int) -> List[Artist]:
    db_artists = self.get_genre_artists(genre_id)
    artist_ids = list(db_artists.keys())
    sp_artists = {a["id"]: a for a in self.get_spotify_artists(artist_ids)}


    artists = []
    for spotify_id in db_artists.keys():
      db_artist = db_artists.get(spotify_id)
      sp_artist = sp_artists.get(spotify_id)

      if sp_artist and db_artist:
        images = [
          ImageObject(
            url=image["url"],
            width=image["width"],
            height=image["height"]
          ) for image in sp_artist['images']
        ]
        artist = Artist(
          id=db_artist["artist"].id,
          spotify_id=spotify_id,
          name=sp_artist["name"],
          bouncyness=db_artist.get("bouncy_value", 0),
          organicness=db_artist.get("organic_value", 0),
          popularity=sp_artist.get("popularity", 0),
          followers=sp_artist["followers"].get("total", 0),
          genres=sp_artist.get("genres", []),
          images=images
        )
        artists.append(artist)

    return artists
