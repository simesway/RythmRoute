from typing import Set, Dict, Optional, Literal, List
from pydantic import BaseModel, Field

from src.models.ArtistHandler import ArtistHandler
from src.models.Sampling import SamplingStrategyType, FilterTypes
from src.models.SongSampler import SongSamplerConfig, SAMPLERS
from src.core.SpotifyCache import Track


MAX_ITERATIONS = 100


class SampledArtists(BaseModel):
  filter: Optional[FilterTypes] = None
  sampler: Optional[SamplingStrategyType] = None
  sampled: Set[int] = Field(default_factory=set)


class SampledTracks(BaseModel):
  sampler: Optional[SongSamplerConfig] = None
  sampled: Set[Track] = Field(default_factory=set)


class SelectedGenre(BaseModel):
  id: int
  artists: SampledArtists = Field(default_factory=SampledArtists)
  tracks: SampledTracks = Field(default_factory=SampledTracks)


class PlaylistFactory(BaseModel):
  genres: Dict[int, SelectedGenre] = Field(default_factory=dict)

  def genre_ids(self):
    return self.genres.keys()

  def add_genre(self, genre_id: int):
    self.genres[genre_id] = SelectedGenre(id=genre_id)

  def remove_genre(self, genre_id: int):
    del self.genres[genre_id]

  def reset(self, genre_id: int, mode: Literal["all", "artists", "tracks"]):
    if mode == "all":
      self.genres[genre_id] = SelectedGenre(id=genre_id)
    elif mode == "artists":
      self.genres[genre_id].artists = SampledArtists()
    elif mode == "tracks":
      self.genres[genre_id].tracks = SampledTracks()

  def sample_artists(self, genre_id: int, sampler: SamplingStrategyType, filter_cls: Optional[FilterTypes] = None, limit: int=20, reset: bool=True):
    if genre_id not in self.genres:
      self.add_genre(genre_id)

    genre = self.genres[genre_id]
    genre.artists.filter = filter_cls
    genre.artists.sampler = sampler
    if reset:
      genre.artists.sampled.clear()

    pool = ArtistHandler().get_pool(genre_id)
    artists = filter_cls(pool.artists) if filter_cls else pool.artists

    for _ in range(MAX_ITERATIONS):
      if len(genre.artists.sampled) >= limit:
        break
      artist = sampler.apply(artists)
      genre.artists.sampled.add(artist.id)

  def sampled_artists(self, genre_id: Optional[int] = None) -> List[int]:
    if genre_id:
      return list(self.genres[genre_id].artists.sampled)
    return [s for genre in self.genres.values() for s in genre.artists.sampled]

  def sample_tracks(self, genre_id: int, sampler_config: SongSamplerConfig, limit: int=20, reset: bool=True):
    genre: SelectedGenre = self.genres[genre_id]
    genre.tracks.sampler = sampler_config
    pool = ArtistHandler().get_pool(genre_id)

    artist_ids = [a.spotify_id for a in pool.artists if a.id in self.genres[genre_id].artists.sampled]
    sampler = SAMPLERS[sampler_config.type](config=sampler_config)
    tracks = sampler.sample(artist_ids, limit)

    if reset:
      genre.tracks.sampled.clear()

    genre.tracks.sampled.update(tracks)

  def sampled_tracks(self, genre_id: Optional[int] = None) -> Set[Track]:
    if genre_id:
      return set(track for track in self.genres[genre_id].tracks.sampled)
    return set(track for genre in self.genres.values() for track in genre.tracks.sampled)

