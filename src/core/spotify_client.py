import logging
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth, SpotifyOauthError
from spotipy.cache_handler import CacheHandler, RedisCacheHandler
from src.core.redis_client import redis_sync
from src.config import SpotifyConfig, SessionConfig

logger = logging.getLogger("SpotifyClient")
logging.basicConfig(level=logging.INFO)


class NoCacheHandler(CacheHandler):
  def get_cached_token(self):
    return None

  def save_token_to_cache(self, token_info):
    pass


class SpotifyClient:
  def __init__(self):
    self.auth_manager = SpotifyClientCredentials(
      client_id=SpotifyConfig.client_id,
      client_secret=SpotifyConfig.client_secret,
      cache_handler=NoCacheHandler()
    )

  def get_spotify_client(self):
    return Spotify(auth_manager=self.auth_manager)


class SpotifyUserClient:
  def __init__(self, user_id):
    self.key = f'spotify:user:token:{user_id}'
    self.cache_handler = RedisCacheHandler(redis_sync, key=self.key)
    self.sp_oauth = self._get_oauth_handler()

  def _reset_expiration(self):
    redis_sync.expire(self.key, SessionConfig.ttl)

  def get_spotify_client(self):
    token_info = self.sp_oauth.validate_token(self.cache_handler.get_cached_token())
    if token_info is None:
      logger.info("No valid token found in cache.")
      return None

    self._reset_expiration()
    return Spotify(auth=token_info['access_token'])

  def get_auth_url(self):
    return self.sp_oauth.get_authorize_url()

  def fetch_and_store_token(self, code):
    try:
      token_info = self.sp_oauth.get_access_token(code, as_dict=True, check_cache=True)
      logger.info(f"Got token.")
      self._reset_expiration()
      return token_info['access_token']
    except SpotifyOauthError as e:
      logger.error(f"Failed to fetch token: {e}")
      return None

  def _get_oauth_handler(self):
    return SpotifyOAuth(
      client_id=SpotifyConfig.client_id,
      client_secret=SpotifyConfig.client_secret,
      redirect_uri=SpotifyConfig.redirect_uri,
      scope=SpotifyConfig.scope,
      cache_handler=self.cache_handler
    )