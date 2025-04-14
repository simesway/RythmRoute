from __future__ import annotations
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy.types import Text
from sqlalchemy import String, ForeignKey, Integer, DateTime, Enum, JSON
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column


class RelationshipTypeEnum(enum.Enum):
  SUBGENRE_OF = "SUBGENRE_OF"
  INFLUENCED_BY = "INFLUENCED_BY"
  FUSION_OF = "FUSION_OF"

class Base(DeclarativeBase):
  pass


class Genre(Base):
  __tablename__ = "genre"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(Text, unique=True)
  normalized_name: Mapped[str] = mapped_column(Text, unique=True)
  description: Mapped[Optional[Text]] = mapped_column(Text)
  popularity: Mapped[Optional[int]] = mapped_column(Integer)
  organic_value: Mapped[Optional[int]]
  bouncy_value: Mapped[Optional[int]]

  mb_id: Mapped[Optional[str]]
  created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)

  artists: Mapped[list["ArtistInGenre"]] = relationship("ArtistInGenre", back_populates="genre")

  def __repr__(self) -> str:
    return self.name

class GenreRelationship(Base):
  __tablename__ = "genre_genre"

  genre1_id: Mapped[int] = mapped_column(Integer, ForeignKey(Genre.id), primary_key=True)
  genre2_id: Mapped[int] = mapped_column(Integer, ForeignKey(Genre.id), primary_key=True)
  relationship: Mapped[RelationshipTypeEnum] = mapped_column(Enum(RelationshipTypeEnum), primary_key=True)

class ImageObject(Base):
  __tablename__ = "image_object"
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  url: Mapped[Text] = mapped_column(Text, nullable=False)
  width: Mapped[Optional[int]]
  height: Mapped[Optional[int]]
  artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"), nullable=False)

  artist: Mapped["Artist"] = relationship("Artist", back_populates="images")

class Artist(Base):
  __tablename__ = "artist"

  id: Mapped[Optional[int]] = mapped_column(primary_key=True, autoincrement=True)
  name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
  spotify_id: Mapped[Optional[str]]
  popularity: Mapped[Optional[int]]
  followers: Mapped[Optional[int]]
  spotify_genres: Mapped[list[str]] = mapped_column(JSON)
  modified_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)

  images: Mapped[list[ImageObject]] = relationship("ImageObject", back_populates="artist")
  genres: Mapped[list["ArtistInGenre"]] = relationship("ArtistInGenre", back_populates="artist")

class ArtistInGenre(Base):
  __tablename__ = "artist_genre"

  genre_id: Mapped[int] = mapped_column(Integer, ForeignKey(Genre.id), primary_key=True)
  artist_id: Mapped[int] = mapped_column(Integer, ForeignKey(Artist.id), primary_key=True)
  organic_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Add explicit column mapping
  bouncy_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Add explicit column mapping

  artist: Mapped[Artist] = relationship("Artist", back_populates="genres")
  genre: Mapped[Genre] = relationship("Genre", back_populates="artists")