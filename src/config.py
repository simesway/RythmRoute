from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class DBConfig(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='db_')
  username: str
  password: str
  host: str
  port: int
  name: str


class RedisConfig(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='redis_')
  host: str
  port: int


class SpotifyConfig(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='spotify_')
  client_id: str
  client_secret: str
  redirect_uri: str
  scope: str
  max_album_batch: int = 20 # limit fixed by spotify web api
  max_artist_batch: int = 50 # limit fixed by spotify web api


class SessionConfig(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='session_')
  cookie_name: str
  ttl: int


class CacheConfig(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='cache_')
  single_object: int = 3600  # 1 hour
  top_tracks: int = 86400 # 1 day
  releases: int = 86400
  album_tracks: int = 86400
  artist_pool: int = 86400
  scrape_time_delta_days: int = 30


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='settings_')
  decimal_precision: int = 6


DBConfig = DBConfig()
RedisConfig = RedisConfig()
SpotifyConfig = SpotifyConfig()
SessionConfig = SessionConfig()
CacheConfig = CacheConfig()
Settings = Settings()