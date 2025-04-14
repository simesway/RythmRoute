from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from tqdm import tqdm

from src.database.db import SessionLocal
from src.database.models import Genre, RelationshipTypeEnum, GenreRelationship, Artist, ArtistInGenre
from src.database.selects import find_matching_genre, find_matching_artist
from src.scraping.MusicBrainz import get_genres, get_genre_page
from src.scraping.every_noise import get_every_sp_genre, get_genre_page_url, get_artists_from_genre_page


def collect_genres_every_noise():
  # Scrape & insert Genres from everynoise map
  genres = get_every_sp_genre()
  with SessionLocal() as session:
    session.add_all(genres)
    session.commit()


def collect_genres_musicbrainz():
  genres = get_genres()

  with SessionLocal() as session:
    for genre in genres:
      matching_genre = find_matching_genre(session, genre.name)
      if not matching_genre:
        session.add(genre)
      else:
        matching_genre.name = genre.name
        matching_genre.mb_id = genre.mb_id

    session.commit()


def collect_genre_relationships_from_mb(genre: Genre):
  """Collects genre relationships and inserts them into the database if they don't exist."""
  relationships = get_genre_page("",mb_id=genre.mb_id)

  relationship_types = {
    "subgenre of": RelationshipTypeEnum.SUBGENRE_OF,
    "subgenre": RelationshipTypeEnum.SUBGENRE_OF,
    "fusion of": RelationshipTypeEnum.FUSION_OF,
    "fusion genre": RelationshipTypeEnum.FUSION_OF,
    "influenced by": RelationshipTypeEnum.INFLUENCED_BY,
    "influenced genre": RelationshipTypeEnum.INFLUENCED_BY,
  }

  with SessionLocal() as session:
    for name, rel_type in relationships:
      related = find_matching_genre(session, name)
      if not related:
        continue  # Skip if related genre doesn't exist

      # Map relationship type to enum
      rel_enum = relationship_types[rel_type]

      if not rel_enum:
        continue  # Skip unknown types

      order = ["subgenre", "fusion genre", "influenced genre"]
      genre1_id, genre2_id = (related.id, genre.id) if rel_type in order else (genre.id, related.id)

      stmt = insert(GenreRelationship).values(
        genre1_id=genre1_id,
        genre2_id=genre2_id,
        relationship=rel_enum
      ).on_conflict_do_nothing()

      session.execute(stmt)

    session.commit()


def collect_artists_from_genre(genre: Genre):
  url = get_genre_page_url(genre.name)
  artists = get_artists_from_genre_page(url)

  with SessionLocal() as session:
    for artist in artists:

      db_artist = find_matching_artist(session, artist["name"])
      if not db_artist:
        db_artist = Artist(name=artist["name"], spotify_id=artist["spotify_id"], spotify_genres=[])
        session.add(db_artist)
        session.flush()
        artist_id = db_artist.id
      else:
        artist_id = db_artist.id

      stmt = insert(ArtistInGenre).values(
        genre_id=genre.id,
        artist_id=artist_id,
        bouncy_value=artist["bouncy_value"],
        organic_value=artist["organic_value"],
      ).on_conflict_do_nothing()

      session.execute(stmt)

    session.commit()


def collect_every_noise(genre_map:bool=True, genre_limit: int=None):
  if genre_map:
    print("collecting EVERY NOISE")
    collect_genres_every_noise()

  with SessionLocal() as session:
    stmt = select(Genre).where(Genre.bouncy_value.isnot(None))
    if genre_limit:
      stmt = stmt.limit(genre_limit)
    genres = session.execute(stmt).scalars().all()

  print("collecting genres:")
  max_iters = 10
  for genre in tqdm(genres):
    for i in range(max_iters):
      try:
        collect_artists_from_genre(genre)
      except Exception as e:
        print(e)
        continue
      break


def collect_musicbrainz():
  print("collecting MUSICBRAINZ")
  collect_genres_musicbrainz()

  with SessionLocal() as session:
    stmt = select(Genre).where(Genre.mb_id.isnot(None))
    genres = session.execute(stmt).scalars().all()

  print("collecting genres:")
  max_iters = 10
  for genre in tqdm(genres):
    for i in range(max_iters):
      try:
        collect_genre_relationships_from_mb(genre)
      except Exception as e:
        print(e)
        continue
      break