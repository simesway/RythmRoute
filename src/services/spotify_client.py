import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from src.services.redis_client import redis_sync
from src.config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIPY_SCOPE, SESSION_USER_EXPIRE_TIME


class SpotifyClient:
  @staticmethod
  def get_spotify_client():
    auth_manager = SpotifyClientCredentials(
      client_id=SPOTIPY_CLIENT_ID,
      client_secret=SPOTIPY_CLIENT_SECRET
    )
    return spotipy.Spotify(auth_manager=auth_manager)



class SpotifyUserClient:
  def __init__(self):
    self.redis = redis_sync
    self.sp_oauth = SpotifyOAuth(
      client_id=SPOTIPY_CLIENT_ID,
      client_secret=SPOTIPY_CLIENT_SECRET,
      redirect_uri=SPOTIPY_REDIRECT_URI,
      scope=SPOTIPY_SCOPE,
      cache_handler=None
    )

  def _get_token(self, user_id):
    token_info = self.redis.hgetall(f'spotify_user_token:{user_id}')
    if token_info and 'access_token' in token_info:
      if self.sp_oauth.is_token_expired(token_info):
        token_info = self.sp_oauth.refresh_access_token(token_info['refresh_token'])
        self._save_token(user_id, token_info)
      return token_info['access_token']
    return None

  def _save_token(self, user_id, token_info):
    name = f'spotify_user_token:{user_id}'
    self.redis.hset(name, mapping=token_info)
    self.redis.expire(name, SESSION_USER_EXPIRE_TIME)

  def get_spotify_client(self, user_id):
    token = self._get_token(user_id)
    if token:
      return spotipy.Spotify(auth=token)
    else:
      raise Exception("No token available. User needs to log in.")

  def get_auth_url(self):
    return self.sp_oauth.get_authorize_url()

  def fetch_and_store_token(self, user_id, response_url):
    token_info = self.sp_oauth.get_access_token(response_url)
    self._save_token(user_id, token_info)
    return token_info['access_token']