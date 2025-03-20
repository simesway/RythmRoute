from src.database.db import SessionLocal
from sqlalchemy import select, and_, or_

from src.database.models import Genre, ArtistInGenre, Artist
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