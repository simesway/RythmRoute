from time import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.cache_handler import CacheHandler
from src.core.redis_client import redis_sync
from src.config import (
  SPOTIPY_CLIENT_ID,
  SPOTIPY_CLIENT_SECRET,
  SPOTIPY_REDIRECT_URI,
  SPOTIPY_SCOPE,
  SESSION_USER_EXPIRE_TIME,
)


class NoCacheHandler(CacheHandler):
  def get_cached_token(self):
    return None

  def save_token_to_cache(self, token_info):
    pass


class SpotifyClient:
  def __init__(self):
    self.auth_manager = SpotifyClientCredentials(
      client_id=SPOTIPY_CLIENT_ID,
      client_secret=SPOTIPY_CLIENT_SECRET,
      cache_handler=NoCacheHandler()
    )

  def get_spotify_client(self):
    return spotipy.Spotify(auth_manager=self.auth_manager)


class RedisCacheHandler(CacheHandler):
  def __init__(self, user_id):
    self.redis = redis_sync
    self.key = f'spotify_user_token:{user_id}'

  def get_cached_token(self):
    token_info = self.redis.hgetall(self.key)
    if not token_info:
      return None
    token_info['expires_at'] = int(token_info['expires_at'])
    return token_info

  def save_token_to_cache(self, token_info):
    token_info['expires_at'] = int(token_info['expires_at'])
    ttl = token_info['expires_at'] - int(time())
    self.redis.hset(self.key, mapping=token_info)
    self.redis.expire(self.key, ttl)


class SpotifyUserClient:
  @staticmethod
  def get_spotify_client(user_id):
    cache_handler = RedisCacheHandler(user_id)
    sp_oauth = SpotifyOAuth(
      client_id=SPOTIPY_CLIENT_ID,
      client_secret=SPOTIPY_CLIENT_SECRET,
      redirect_uri=SPOTIPY_REDIRECT_URI,
      scope=SPOTIPY_SCOPE,
      cache_handler=cache_handler
    )

    token_info = cache_handler.get_cached_token()
    if token_info and 'access_token' in token_info:
      if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        cache_handler.save_token_to_cache(token_info)
      return spotipy.Spotify(auth=token_info['access_token'])

    return None

  @staticmethod
  def get_auth_url(user_id):
    sp_oauth = SpotifyOAuth(
      client_id=SPOTIPY_CLIENT_ID,
      client_secret=SPOTIPY_CLIENT_SECRET,
      redirect_uri=SPOTIPY_REDIRECT_URI,
      scope=SPOTIPY_SCOPE,
      cache_handler=RedisCacheHandler(user_id)
    )
    return sp_oauth.get_authorize_url()

  @staticmethod
  def fetch_and_store_token(user_id, code):
    cache_handler = RedisCacheHandler(user_id)
    sp_oauth = SpotifyOAuth(
      client_id=SPOTIPY_CLIENT_ID,
      client_secret=SPOTIPY_CLIENT_SECRET,
      redirect_uri=SPOTIPY_REDIRECT_URI,
      scope=SPOTIPY_SCOPE,
      cache_handler=cache_handler
    )
    token_info = sp_oauth.get_access_token(code, as_dict=True, check_cache=False)
    cache_handler.save_token_to_cache(token_info)
    return token_info['access_token']
