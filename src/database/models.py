from typing import Optional

from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column

class Base(DeclarativeBase):
  pass

class Genre(Base):
  __tablename__ = "genre"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(50))
  organic_value: Mapped[int]
  bouncy_value: Mapped[int]

  artists: Mapped[list["ArtistInGenre"]] = relationship("ArtistInGenre", back_populates="genre")

class Artist(Base):
  __tablename__ = "artist"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
  spotify_id: Mapped[Optional[int]]

  genres: Mapped[list["ArtistInGenre"]] = relationship("ArtistInGenre", back_populates="artist")

class ArtistInGenre(Base):
  __tablename__ = "artist_genre"

  genre_id: Mapped[int] = mapped_column(Integer, ForeignKey(Genre.id), primary_key=True)
  artist_id: Mapped[int] = mapped_column(Integer, ForeignKey(Artist.id), primary_key=True)
  organic_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Add explicit column mapping
  bouncy_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Add explicit column mapping

  artist: Mapped[Artist] = relationship("Artist", back_populates="genres")
  genre: Mapped[Genre] = relationship("Genre", back_populates="artists")