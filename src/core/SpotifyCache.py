import json
from pydantic import BaseModel, Field
from spotipy import SpotifyException
from typing import List, Literal, Optional, Type
import logging

from src.config import CacheConfig, SpotifyConfig
from src.core.redis_client import redis_sync
from src.core.spotify_client import SpotifyClient, SpotifyUserClient

logger = logging.getLogger(__name__)

AlbumType = Literal['album', 'compilation', 'ep', 'single']
Exceptions = (SpotifyException, Exception)


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


class Release(SpotifyModel):
  artist_ids: List[str] =  Field(default_factory=list)


class Album(Release):
  type: AlbumType
  release_date: str
  total_tracks: int
  images: List[ImageObject] = Field(default_factory=list)
  popularity: Optional[int]

  class Config:
    use_enum_values = True


class Track(Release):
  album_id: str
  duration: int
  popularity: Optional[int]

  def __hash__(self) -> int:
    return hash((self.name, tuple(sorted(self.artist_ids))))

  def __eq__(self, other) -> bool:
    if not isinstance(other, self.__class__):
      return False
    return self.id == other.id or (self.name == other.name and set(self.artist_ids) == set(other.artist_ids))


class Artist(SpotifyModel):
  popularity: Optional[int]
  genres: List[str] = Field(default_factory=list)
  images: List[ImageObject] = Field(default_factory=list)


class SpotifyUser(SpotifyModel):
  images: List[ImageObject] = Field(default_factory=list)


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
      images=DataConverter.to_image_objects(album_data['images']),
      popularity=album_data.get('popularity', None)
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
  def to_user(user_data: dict) -> SpotifyUser:
    return SpotifyUser(
      id=user_data['id'],
      name=user_data['display_name'] or "",
      images=DataConverter.to_image_objects(user_data['images'])
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

  def get_current_user(self, session_id: str) -> Optional[SpotifyUser]:
    key = f"spotify:user:{session_id}"
    data = self.redis.get(key)

    if data:
      return SpotifyUser.model_validate_json(data)

    try:
      sp = SpotifyUserClient(session_id).get_spotify_client()
      if sp is None:
        return None
      logger.info("Caching Spotify User")
      data = self.converter.to_user(sp.me())
      self.redis.setex(key, CacheConfig.single_object, data.model_dump_json())
      return data
    except SpotifyException as e:
        logger.warning(f"SpotifyException in get_track: {e}")
    except Exception as e:
        logger.error(f"Unhandled error in get_track: {e}")
    return None

  def get_track(self, track_id: str) -> Optional[Track]:
    key = f"track:{track_id}"
    data = self.redis.get(key)
    if data:
        return Track.model_validate_json(data)
    try:
        logger.info(f"Caching Track: {track_id}")
        track = self.spotify.track(track_id)
        data = self.converter.to_track(track)
        self.redis.setex(key, CacheConfig.single_object, data.model_dump_json())
        return data
    except SpotifyException as e:
        logger.warning(f"SpotifyException in get_track: {e}")
    except Exception as e:
        logger.error(f"Unhandled error in get_track: {e}")
    return None

  def get_album(self, album_id: str) -> Optional[Album]:
    key = f"album:{album_id}"
    data = self.redis.get(key)
    if data:
      return Album.model_validate_json(data)

    try:
      logger.info(f"Caching Album: {album_id}")
      album = self.spotify.album(album_id)
      data = self.converter.to_album(album)
      self.redis.setex(key, CacheConfig.single_object, data.model_dump_json())
      return data
    except SpotifyException as e:
        logger.warning(f"SpotifyException in get_album: {e}")
    except Exception as e:
        logger.error(f"Unhandled error in get_album: {e}")
    return None

  def get_artist(self, artist_id: str) -> Optional[Artist]:
    key = f"artist:{artist_id}"
    data = self.redis.get(key)
    if data:
      return Artist.model_validate_json(data)

    try:
      logger.info(f"Caching Artist: {artist_id}")
      artist = self.spotify.artist(artist_id)
      data = self.converter.to_artist(artist)
      self.redis.setex(key, CacheConfig.single_object, data.model_dump_json())
      return data
    except SpotifyException as e:
      logger.warning(f"SpotifyException in get_artist: {e}")
    except Exception as e:
      logger.error(f"Unhandled error in get_artist: {e}")
    return None

  def get_albums(self, album_ids: List[str]) -> List[Album]:
    keys = [f"album:{aid}" for aid in album_ids]
    cached_data = self.redis.mget(keys)

    results = []
    uncached_ids = []

    for album_id, data in zip(album_ids, cached_data):
      if data:
        results.append(Album.model_validate_json(data))
      else:
        uncached_ids.append(album_id)

    for i in range(0, len(uncached_ids), SpotifyConfig.max_album_batch):
      batch = uncached_ids[i:i+SpotifyConfig.max_album_batch]
      logger.info(f"Caching Album Batch: {batch}")
      try:
        fetched = self.spotify.albums(batch)['albums']
        converted = [self.converter.to_album(a) for a in fetched]
        for album in converted:
          self.redis.setex(f"album:{album.id}", CacheConfig.single_object, album.model_dump_json())
        results.extend(converted)
      except SpotifyException as e:
        logger.warning(f"SpotifyException in get_albums: {e}")
        continue

    return results

  def get_artists(self, artist_ids: List[str]) -> List[Artist]:
    keys = [f"artist:{aid}" for aid in artist_ids]
    cached_data = self.redis.mget(keys)

    results = []
    uncached_ids = []

    for artist_id, data in zip(artist_ids, cached_data):
      if data:
        results.append(Artist.model_validate_json(data))
      else:
        uncached_ids.append(artist_id)

    for i in range(0, len(uncached_ids), SpotifyConfig.max_artist_batch):
      batch = uncached_ids[i:i+SpotifyConfig.max_artist_batch]
      logger.info(f"Caching Artist Batch: {batch}")
      try:
        fetched = self.spotify.artists(batch)['artists']
        converted = [self.converter.to_artist(a) for a in fetched]
        for artist in converted:
          self.redis.setex(f"artist:{artist.id}", CacheConfig.single_object, artist.model_dump_json())
        results.extend(converted)
      except SpotifyException as e:
        logger.warning(f"SpotifyException in get_artists: {e}")
        continue

    return results

  def get_top_tracks(self, artist_id: str) -> List[Track]:
    key = f"artist:top_tracks:{artist_id}"
    data = self.redis.get(key)
    if data:
      return self.converter.deserialize(Track, data)

    try:
      logger.info(f"Caching Top Tracks: {artist_id}")
      tracks = self.spotify.artist_top_tracks(artist_id)['tracks']
      data = [self.converter.to_track(t) for t in tracks]
      self.redis.setex(key, CacheConfig.top_tracks, self.converter.serialize(data))
      return data
    except SpotifyException as e:
      logger.warning(f"SpotifyException in get_top_tracks: {e}")
    except Exception as e:
      logger.error(f"Unhandled error in get_top_tracks: {e}")
    return []

  def get_releases(self, artist_id: str) -> List[Album]:
    key = f"artist:releases:{artist_id}"
    data = self.redis.get(key)
    if data:
      return self.converter.deserialize(Album, data)

    try:
      logger.info(f"Caching Releases: {artist_id}")
      albums = self.spotify.artist_albums(
        artist_id,
        include_groups='album,compilation,single,ep'
      )['items']
      data = [self.converter.to_album(a) for a in albums]
      self.redis.setex(key, CacheConfig.releases, self.converter.serialize(data))
      return data
    except SpotifyException as e:
      logger.warning(f"SpotifyException in get_releases: {e}")
    except Exception as e:
      logger.error(f"Unhandled error in get_releases: {e}")
    return []

  def get_album_tracks(self, album_id: str) -> List[Track]:
    key = f"album:tracks:{album_id}"
    data = self.redis.get(key)

    if data:
      return self.converter.deserialize(Track, data)
    try:
      tracks = self.spotify.album_tracks(album_id)['items']
      logger.info(f"Caching Album Tracks: {album_id}")
      data = [self.converter.to_track(t, album_id) for t in tracks]
      self.redis.setex(key, CacheConfig.album_tracks, self.converter.serialize(data))
      return data
    except SpotifyException as e:
      logger.warning(f"SpotifyException in get_album_tracks: {e}")
    except Exception as e:
      logger.error(f"Unhandled error in get_album_tracks: {e}")
    return []