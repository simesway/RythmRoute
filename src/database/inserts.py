from typing import Union, List, Dict
from db import SessionLocal
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert


from src.database.models import Artist, ArtistInGenre


def get_or_create_artist_ids(artists: List[Dict[str, Union[str, int]]], as_dict: bool=True):
  """Get IDs for existing artists and insert new ones, also returning new IDs."""
  with SessionLocal() as session:
    existing = session.execute(
      select(Artist.id, Artist.name)
      .where(Artist.name.in_([artist["name"] for artist in artists]))
    ).all()
    session.commit()

  existing_artists = {row.name: row.id for row in existing}
  new_artists = [artist for artist in artists if artist["name"] not in existing_artists]

  with SessionLocal() as session:
    if len(new_artists) > 0:
      stmt = (
        insert(Artist)
        .values(new_artists)
        .on_conflict_do_nothing(
          index_elements=[Artist.name])
        .returning(Artist.id, Artist.name)
      )
      new_artists = session.execute(stmt).all()
      session.commit()

    if as_dict:
      return {artist.name: artist.id for artist in existing + new_artists}
    return existing + new_artists.all()

def add_artists_to_genre(genre_id: int, artists: Dict[str, int]):
  print(artists)
  with SessionLocal() as session:
    stmt = (
      insert(ArtistInGenre)
      .values([{
        "genre_id": genre_id,
        "artist_id": a["id"],
        "bouncy_value": a["bouncy_value"],
        "organic_value": a["organic_value"]}
    for a in artists
      ]).on_conflict_do_nothing()
    )
    session.execute(stmt)
    session.commit()