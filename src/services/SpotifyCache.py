import json
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Type, TypeVar
from src.services.redis_client import redis_sync
from src.services.spotify_client import SpotifyClient


class CacheConfig:
  SINGLE_OBJECT_TTL = 86400  # 1 day
  TOP_TRACKS_TTL = 86400
  ALBUMS_TTL = 86400
  ALBUM_TRACKS_TTL = 86400


class AlbumType(Enum):
  ALBUM = 'album'
  COMPILATION = 'compilation'
  EP = 'ep'
  SINGLE = 'single'


class SpotifyModel(BaseModel):
  id: str
  name: str

  def __repr__(self):
    return self.name

  def __eq__(self, other) -> bool:
    return isinstance(other, self.__class__) and self.id == other.id

  def __hash__(self) -> int:
    return hash(self.id)


class ImageObject(BaseModel):
  url: str
  width: Optional[int] = None
  height: Optional[int] = None


class Album(SpotifyModel):
  type: AlbumType
  release_date: str
  total_tracks: int
  artist_ids: List[str] = []
  images: List[ImageObject] = []

  class Config:
    use_enum_values = True


class Track(SpotifyModel):
  album_id: str
  duration: int
  popularity: Optional[int]
  artist_ids: List[str]

  def __hash__(self) -> int:
    return hash((self.name, tuple(sorted(self.artist_ids))))

  def __eq__(self, other) -> bool:
    if not isinstance(other, self.__class__):
      return False
    return self.id == other.id or (self.name == other.name and set(self.artist_ids) == set(other.artist_ids))


class Artist(SpotifyModel):
  popularity: Optional[int]
  genres: List[str] = []
  images: List[ImageObject] = []


class DataConverter:
  @staticmethod
  def to_image_objects(images: List[dict]) -> List[ImageObject]:
    return [ImageObject(
      url=img['url'],
      width=img['width'] or None,
      height=img['height'] or None
    ) for img in images]

  @staticmethod
  def to_track(track_data: dict, album_id: str = None) -> Track:
    return Track(
      id=track_data['id'],
      name=track_data['name'],
      artist_ids=[artist['id'] for artist in track_data['artists']],
      album_id=album_id or track_data['album']['id'],
      duration=track_data['duration_ms'],
      popularity=track_data.get('popularity')
    )

  @staticmethod
  def to_album(album_data: dict) -> Album:
    return Album(
      id=album_data['id'],
      name=album_data['name'],
      type=album_data['album_type'],
      total_tracks=album_data['total_tracks'],
      release_date=album_data['release_date'],
      artist_ids=[a['id'] for a in album_data['artists']],
      images=DataConverter.to_image_objects(album_data['images'])
    )

  @staticmethod
  def to_artist(artist_data: dict) -> Artist:
    return Artist(
      id=artist_data['id'],
      name=artist_data['name'],
      popularity=artist_data.get('popularity'),
      genres=artist_data.get('genres', []),
      images=DataConverter.to_image_objects(artist_data['images'])
    )

  @staticmethod
  def serialize(items: List[BaseModel]) -> str:
    return json.dumps([item.model_dump() for item in items])

  @staticmethod
  def deserialize(cls: Type[BaseModel], data: str) -> List[BaseModel]:
    return [cls.model_validate(item) for item in json.loads(data)]


class SpotifyCache:
  def __init__(self):
    self.redis = redis_sync
    self.spotify = SpotifyClient().get_spotify_client()
    self.converter = DataConverter()

  def get_track(self, track_id: str) -> Track:
    key = f"track:{track_id}"
    data = self.redis.get(key)

    if data:
      return Track.model_validate_json(data)

    track = self.spotify.track(track_id)
    data = self.converter.to_track(track)
    self.redis.setex(key, CacheConfig.SINGLE_OBJECT_TTL, data.model_dump_json())
    return data

  def get_album(self, album_id: str) -> Album:
    key = f"album:{album_id}"
    data = self.redis.get(key)

    if data:
      return Album.model_validate_json(data)

    album = self.spotify.album(album_id)
    data = self.converter.to_album(album)
    self.redis.setex(key, CacheConfig.SINGLE_OBJECT_TTL, data.model_dump_json())
    return data

  def get_artist(self, artist_id: str) -> Artist:
    key = f"artist:{artist_id}"
    data = self.redis.get(key)

    if data:
      return Artist.model_validate_json(data)

    artist = self.spotify.artist(artist_id)
    data = self.converter.to_artist(artist)
    self.redis.setex(key, CacheConfig.SINGLE_OBJECT_TTL, data.model_dump_json())
    return data

  def get_top_tracks(self, artist_id: str) -> List[Track]:
    key = f"artist:top_tracks:{artist_id}"
    data = self.redis.get(key)

    if data:
      return self.converter.deserialize(Track, data)

    tracks = self.spotify.artist_top_tracks(artist_id)['tracks']
    data = [self.converter.to_track(t) for t in tracks]
    self.redis.setex(key, CacheConfig.TOP_TRACKS_TTL, self.converter.serialize(data))
    return data

  def get_releases(self, artist_id: str) -> List[Album]:
    key = f"artist:releases:{artist_id}"
    data = self.redis.get(key)

    if data:
      return self.converter.deserialize(Album, data)

    albums = self.spotify.artist_albums(
      artist_id,
      include_groups='album,compilation,single,ep'
    )['items']
    data = [self.converter.to_album(a) for a in albums]
    self.redis.setex(key, CacheConfig.ALBUMS_TTL, self.converter.serialize(data))
    return data

  def get_album_tracks(self, album_id: str) -> List[Track]:
    key = f"album:tracks:{album_id}"
    data = self.redis.get(key)

    if data:
      return self.converter.deserialize(Track, data)

    tracks = self.spotify.album_tracks(album_id)['items']
    data = [self.converter.to_track(t, album_id) for t in tracks]
    self.redis.setex(key, CacheConfig.ALBUM_TRACKS_TTL, self.converter.serialize(data))
    return data