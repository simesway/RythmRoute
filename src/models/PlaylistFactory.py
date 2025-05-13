from dataclasses import field
from typing import Set, Dict, Optional
from pydantic import BaseModel

from src.models.ArtistHandler import ArtistHandler
from src.models.Sampling import SamplingStrategyType, AttributeWeightedSampling
from src.models.SongSampler import SongSamplerConfig, SAMPLERS, TopSongsConfig
from src.services.SpotifyCache import Track


MAX_ITERATIONS = 100


class SampledArtists(BaseModel):
  strategy: Optional[SamplingStrategyType] = None
  sampled: Set[int] = field(default_factory=set)


class SampledTracks(BaseModel):
  strategy: Optional[SongSamplerConfig] = None
  sampled: Set[Track] = field(default_factory=set)


class SelectedGenre(BaseModel):
  id: int
  artists: SampledArtists = SampledArtists()
  tracks: SampledTracks = SampledTracks()


class PlaylistFactory(BaseModel):
  genres: Dict[int, SelectedGenre] = field(default_factory=dict)

  def add_genre(self, genre_id: int):
    self.genres[genre_id] = SelectedGenre(id=genre_id)

  def remove_genre(self, genre_id: int):
    del self.genres[genre_id]

  def sample_artists(self, genre_id: int, sampler: SamplingStrategyType, limit: int=20, reset: bool=True):
    if genre_id not in self.genres:
      self.add_genre(genre_id)

    genre = self.genres[genre_id]
    genre.artists.strategy = sampler
    if reset:
      genre.artists.sampled.clear()

    pool = ArtistHandler().get_pool(genre_id)

    for _ in range(MAX_ITERATIONS):
      if len(genre.artists.sampled) >= limit:
        break
      artist = sampler.apply(pool.artists)
      genre.artists.sampled.add(artist.id)

  def sample_tracks(self, genre_id: int, sampler_config: SongSamplerConfig, limit: int=20, reset: bool=True):
    genre = self.genres[genre_id]
    genre.tracks.strategy = sampler_config
    pool = ArtistHandler().get_pool(genre_id)

    artist_ids = [a.spotify_id for a in pool.artists if a.id in self.genres[genre_id].artists.sampled]
    sampler = SAMPLERS[sampler_config.type](config=sampler_config)
    tracks = sampler.sample(artist_ids, limit)

    if reset:
      genre.tracks.sampled.clear()

    genre.tracks.sampled.update(tracks)
