from src.core.db import SessionLocal
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import aliased

from src.database.models import Genre, ArtistInGenre, Artist, RelationshipTypeEnum, GenreRelationship
from src.scraping.helper import normalize_genre_name


def get_genres_in_range(bouncy_range, organic_range):
  with SessionLocal() as session:
    stmt = select(Genre).where(
      and_(
        Genre.bouncy_value.between(bouncy_range[0], bouncy_range[1]),
        Genre.organic_value.between(organic_range[0], organic_range[1])
      )
    )

    result = session.execute(stmt).scalars().all()
    session.commit()
    return [{"name": r.name, "id": r.id} for r in result]



def get_artists_from_genre(genre):
  with SessionLocal() as session:
    stmt = select(Genre).where(Genre.name == genre).join(ArtistInGenre)
    result = session.execute(stmt).all()
    session.commit()
    return result


def find_matching_genre(session, genre: str):
  norm_space, norm_hyphen = normalize_genre_name(genre)
  genre = session.query(Genre).filter(
    or_(Genre.normalized_name.ilike(norm_space), Genre.normalized_name.ilike(norm_hyphen))
  ).first()
  return genre

def find_matching_artist(session, artist: str):
  return session.query(Artist).filter(Artist.name == artist).first()

def get_all_mb_genres(session):
  stmt = select(Genre).filter(Genre.mb_id.isnot(None))
  return session.execute(stmt).all()

def get_all_relationships(session):
  stmt = select(GenreRelationship)
  return session.execute(stmt).all()

def get_all_genre_relationships(session, relationship_type: RelationshipTypeEnum):
  g1 = aliased(Genre)
  g2 = aliased(Genre)
  stmt = (
    select(
      g1, GenreRelationship.relationship, g2
    ).where(GenreRelationship.relationship == relationship_type)
    .join(g1, g1.id == GenreRelationship.genre1_id)
    #.where(g1.organic_value < 2800)
    .join(g2, g2.id == GenreRelationship.genre2_id)
    #.where(g1.organic_value < 2800)
  )

  relationships = session.execute(stmt).all()
  return relationships

def get_main_genres(session):
  """Fetch genres that don't appear as id2 (i.e., they aren't subgenres)."""
  subquery = session.query(GenreRelationship.genre1_id).distinct()
  return session.query(Genre).where(Genre.mb_id != None).filter(Genre.id.not_in(subquery)).all()


def get_subgenres(session, genre_id):
  g1 = aliased(Genre)
  g2 = aliased(Genre)
  stmt = (
    select(g1, GenreRelationship.relationship)
    .join(g1, g1.id == GenreRelationship.genre1_id)
    .join(g2, g2.id == GenreRelationship.genre2_id)
    .where(g2.id == genre_id)
  )
  relationships = session.execute(stmt).all()
  return relationships


def get_related_genres(session, genre_id):
  """Fetch genres connected to a given genre by any relationship type."""
  return (
    session.query(Genre, GenreRelationship.type)
    .join(GenreRelationship, Genre.id == GenreRelationship.id2)
    .filter(GenreRelationship.id1 == genre_id)
    .all()
  )