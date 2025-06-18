from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class DBConfig(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='db_')
  username: str
  password: str
  host: str
  port: int
  name: str

DB_SCRAPE_TIME_DELTA_DAYS = os.getenv("DB_SCRAPE_TIME_DELTA_DAYS")

class RedisConfig(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='redis_')
  host: str
  port: int

DBConfig = DBConfig()
RedisConfig = RedisConfig()

class SpotifyConfig(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='spotify_')
  client_id: str
  client_secret: str
  redirect_uri: str
  scope: str
  max_album_batch: int = 20 # limit fixed by spotify web api
  max_artist_batch: int = 50 # limit fixed by spotify web api

SpotifyConfig = SpotifyConfig()

class SessionConfig(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='session_')
  cookie_name: str
  ttl: int

SessionConfig = SessionConfig()

class CacheConfig(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='cache_')
  single_object: int = 3600  # 1 hour
  top_tracks: int = 86400 # 1 day
  releases: int = 86400
  album_tracks: int = 86400
  artist_pool: int = 86400
  scrape_time_delta_days: int = 30

CacheConfig = CacheConfig()

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_prefix='settings_')
  decimal_precision: int = 6

Settings = Settings()

DEC_PREC = int(os.getenv("DEC_PREC"))