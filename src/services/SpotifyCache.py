import json
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

from src.services.redis_client import redis_sync
from src.services.spotify_client import SpotifyClient


TOP_TRACKS_CACHE_TIME = 86400 # 1 DAY
ALBUMS_CACHE_TIME = 2592000 # 30 DAYS
ALBUM_TRACKS_CACHE_TIME = 2592000 # 30 DAYS


class AlbumType(Enum):
  ALBUM = 'album'
  COMPILATION = 'compilation'
  EP = 'ep'
  SINGLE = 'single'

class ImageObject(BaseModel):
  url: str
  width: Optional[int] = None
  height: Optional[int] = None

class Album(BaseModel):
  id: str
  name: str
  type: AlbumType
  release_date: str
  total_tracks: int
  artist_ids: List[str] = []
  images: List[ImageObject] = []

  class Config:
    use_enum_values = True

class Track(BaseModel):
  id: str
  name: str
  album_id: str
  duration: int
  popularity: Optional[int]
  artist_ids: List[str]


class SpotifyCache:
  def __init__(self):
    self.r = redis_sync
    self.sp = SpotifyClient().get_spotify_client()

  @staticmethod
  def _convert_to_img_obj(images) -> List[ImageObject]:
    return [ImageObject(
      url=i['url'],
      width=i['width'] or None,
      height=i['height'] or None
    ) for i in images ]

  @staticmethod
  def _convert_to_track(t: dict, album_id: str = None):
    return Track(
      id=t['id'],
      name=t['name'],
      artist_ids=[a['id'] for a in t['artists']],
      album_id=album_id or t['album']['id'],
      duration=t['duration_ms'],
      popularity=t.get('popularity', None)
    )

  @staticmethod
  def _serialize(items):
    return json.dumps([i.model_dump() for i in items])

  @staticmethod
  def _deserialize(cls, data: str):
    return [cls.model_validate(item) for item in json.loads(data)]

  def _get_data(self, cls, key):
    data = self.r.get(key)
    if data:
      return self._deserialize(cls, data)
    return None

  def get_top_tracks(self, artist_id: str) -> List[Track]:
    key = f"artist:top_tracks:{artist_id}"
    data = self._get_data(Track, key)

    if not data:
      tracks = self.sp.artist_top_tracks(artist_id)['tracks']
      data = [self._convert_to_track(t) for t in tracks]

      self.r.setex(key, TOP_TRACKS_CACHE_TIME, self._serialize(data))
    return data

  def get_releases(self, artist_id: str) -> List[Album]:
    key = f"artist:releases:{artist_id}"
    data = self._get_data(Album, key)

    if not data:
      albums = self.sp.artist_albums(artist_id, include_groups='album,compilation,single,ep')['items']
      data = [Album(
        id=a['id'],
        name=a['name'],
        type=a['album_type'],
        total_tracks=a['total_tracks'],
        release_date=a['release_date'],
        artist_ids=[a['id'] for a in a['artists']],
        images=self._convert_to_img_obj(a['images'])
      ) for a in albums]

      self.r.setex(key, ALBUMS_CACHE_TIME, self._serialize(data))
    return data

  def get_album_tracks(self, album_id: str) -> List[Track]:
    key = f"album:tracks:{album_id}"
    data = self._get_data(Album, key)

    if not data:
      tracks = self.sp.album_tracks(album_id)['items']
      data = [self._convert_to_track(t, album_id) for t in tracks]

      self.r.setex(key, ALBUM_TRACKS_CACHE_TIME, self._serialize(data))
    return data