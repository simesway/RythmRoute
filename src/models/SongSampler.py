from abc import ABC, abstractmethod
from src.services.SpotifyCache import Album, Track, SpotifyCache, Release
from typing import Dict, List, Set, Union
from collections import defaultdict
from datetime import datetime
import numpy as np
import math
import random
from pydantic import BaseModel

NON_CORE_KEYWORDS = [
  "remix", "live", "deluxe", "instrumental",
  "karaoke", "acoustic", "demo", "commentary",
  "bonus", "edit", "version", "reissue",
  "mix", "intro", "outro", "skit", "prolog",
  "interlude", "revisited"
]

class SongSamplerConfig(BaseModel):
  type: str

class SongSampler(ABC):
  def __init__(self, config: SongSamplerConfig) -> None:
    self.config = config
    self.sp = SpotifyCache()


  @staticmethod
  def is_core_release(release: Release, artist_id: str=None) -> bool:
    from_main_artist = artist_id == release.artist_ids[0] if artist_id else True
    name = release.name.lower()
    contains_keywords = any(keyword in name for keyword in NON_CORE_KEYWORDS)
    return from_main_artist and not contains_keywords

  def sample(self, artist_ids: List[str], num: int = 5) -> Set[Track]:
    if not artist_ids or num <= 0:
      return set()

    if num < len(artist_ids):
      return self.sample_evenly_across_artists(artist_ids, num)
    else:
      return self.sample_multiple_per_artist(artist_ids, num)

  @abstractmethod
  def sample_evenly_across_artists(self, artist_ids: List[str], num: int) -> Set[Track]:
    raise NotImplementedError

  @abstractmethod
  def sample_multiple_per_artist(self, artist_ids: List[str], num: int) -> Set[Track]:
    raise NotImplementedError

class StrategyWeightPair(BaseModel):
  strategy: 'SamplerConfigUnion'
  weight: float

class CombinedSamplerConfig(SongSamplerConfig):
  type: str = "combined"
  strategies: List[StrategyWeightPair]

class CombinedSongSampler:
  def __init__(self, config: CombinedSamplerConfig):
    self.config = config

  def sample(self, artist_ids: List[str], num: int) -> Set[Track]:
    sampled_tracks = set()
    total_weight = sum(strategy.weight for strategy in self.config.strategies)
    for pair in self.config.strategies:
      sampler_cls = SAMPLERS[pair.strategy.type]
      sampler: SongSampler = sampler_cls(config=pair.strategy)
      portion = round(num * (pair.weight / total_weight))
      tracks = sampler.sample(artist_ids, portion)
      sampled_tracks.update(tracks)
    return sampled_tracks

class TopSongsConfig(SongSamplerConfig):
  type: str = "top_songs"

class TopSongsSampler(SongSampler):
  def sample_evenly_across_artists(self, artist_ids: List[str], num: int) -> Set[Track]:
    sampled_artists = random.sample(artist_ids, num)
    sampled_tracks = set()

    for artist_id in sampled_artists:
      top_tracks = self.sp.get_top_tracks(artist_id)
      if top_tracks:
        sampled_tracks.add(random.choice(top_tracks))

    return sampled_tracks

  def sample_multiple_per_artist(self, artist_ids: List[str], num: int, max_iter: int=1000) -> Set[Track]:
    if num > len(artist_ids) * 10:
      num = len(artist_ids) * 10

    artist_to_tracks = {
      artist_id: set(self.sp.get_top_tracks(artist_id))
      for artist_id in set(artist_ids)
    }
    available_artists = [aid for aid, tracks in artist_to_tracks.items() if tracks]

    if not available_artists:
      return set()

    sampled_tracks = set()
    while len(sampled_tracks) < num and max_iter > 0:
      artist_id = available_artists[max_iter % len(available_artists)]
      top_tracks = artist_to_tracks[artist_id]
      if len(top_tracks) > 0:
        track = top_tracks.pop()
        sampled_tracks.add(track)
      max_iter -= 1

    return sampled_tracks

class RandomReleaseConfig(SongSamplerConfig):
  type: str = "random_release"

class RandomReleaseSongSampler(SongSampler):
  def sample_evenly_across_artists(self, artist_ids: List[str], num: int) -> Set[Track]:
    sampled_artists = random.sample(artist_ids, num)

    sampled_tracks = set()
    for artist_id in sampled_artists:
      releases = self.sp.get_releases(artist_id)
      if not releases:
        continue
      release = random.choice(releases)
      track = random.choice(self.sp.get_album_tracks(release.id))
      sampled_tracks.add(track)

    return sampled_tracks

  def sample_multiple_per_artist(self, artist_ids: List[str], num: int, max_iter: int=1000) -> Set[Track]:
    artist_to_releases = {
      artist_id: self.sp.get_releases(artist_id)
      for artist_id in set(artist_ids)
    }
    available_artists = [aid for aid, releases in artist_to_releases.items() if releases]

    if not available_artists:
      return set()

    sampled_tracks = set()
    while len(sampled_tracks) < num and max_iter > 0:
      artist_id = available_artists[max_iter % len(available_artists)]
      release = random.choice(artist_to_releases[artist_id])
      tracks = self.sp.get_album_tracks(release.id)
      if tracks:
        track = random.choice(tracks)
        sampled_tracks.add(track)
      max_iter -= 1

    return sampled_tracks

class AlbumClusterConfig(SongSamplerConfig):
  type: str = "album_cluster"
  exclude_types: List[str]
  core_only: bool

class AlbumClusterSampler(SongSampler):
  @staticmethod
  def cluster_releases(releases: List[Album]) -> Dict[str, List[Album]]:
    clusters = defaultdict(list)
    for release in releases:
      clusters[release.type].append(release)
    return dict(clusters)

  def sample_from_release_clusters(self, artist_ids: List[str], num: int = 5, max_iter: int = 1000) -> Set[Track]:
    releases = [
      release for artist_id in artist_ids
      for release in self.sp.get_releases(artist_id) or [] if not self.config.core_only or self.is_core_release(release, artist_id)
    ]
    if not releases:
      return set()

    clusters = self.cluster_releases(releases)
    filtered = {k: v for k, v in clusters.items() if k not in self.config.exclude_types}
    if not filtered:
      return set()

    sampled_tracks = set()
    while len(sampled_tracks) < num and max_iter > 0:
      release_type = random.choice(list(filtered))
      release = random.choice(filtered[release_type])
      tracks = self.sp.get_album_tracks(release.id) or []
      tracks = [track for track in tracks if not self.config.core_only or self.is_core_release(track)]
      if tracks:
        sampled_tracks.add(random.choice(tracks))
      max_iter -= 1

    return sampled_tracks

  def sample_evenly_across_artists(self, artist_ids: List[str], num: int, max_iter: int=1000) -> Set[Track]:
    sampled_artists = random.sample(artist_ids, num)
    sampled_tracks = self.sample_from_release_clusters(sampled_artists, num=num)
    return sampled_tracks

  def sample_multiple_per_artist(self, artist_ids: List[str], num: int) -> Set[Track]:
    sampled_tracks = self.sample_from_release_clusters(artist_ids, num=num)
    return sampled_tracks

class FullTrackPoolConfig(SongSamplerConfig):
  type: str = "full_track_pool"
  core_only: bool

class FullTrackPoolSampler(SongSampler):
  def sample_from_full_track_pool(self, artist_ids: List[str], num: int) -> Set[Track]:
    releases = [
      release for artist_id in artist_ids
      for release in self.sp.get_releases(artist_id) or [] if not self.config.core_only or self.is_core_release(release, artist_id)
    ]
    tracks = set(
      track for release in releases for track in self.sp.get_album_tracks(release.id)
      if not self.config.core_only or self.is_core_release(track)
    )

    if not tracks:
      return set()

    if len(tracks) <= num:
      return tracks

    return random.sample(list(tracks), num)

  def sample_evenly_across_artists(self, artist_ids: List[str], num: int) -> Set[Track]:
    return self.sample_from_full_track_pool(artist_ids, num=num)

  def sample_multiple_per_artist(self, artist_ids: List[str], num: int) -> Set[Track]:
    return self.sample_from_full_track_pool(artist_ids, num=num)

class NearestReleaseDateConfig(SongSamplerConfig):
  type: str = "nearest_release_date"
  target_date: datetime
  sigma_days: float
  core_only: bool = True

class NearestReleaseDateSampler(SongSampler):
  @staticmethod
  def parse_release_date_flexible(release_date: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
      try:
        return datetime.strptime(release_date, fmt)
      except ValueError:
        continue
    raise ValueError(f"Unknown release_date format: {release_date}")

  def compute_weight(self, release_date: datetime) -> float:
    delta_days = abs((release_date - self.config.target_date).days)
    return math.exp(- (delta_days ** 2) / (2 * self.config.sigma_days ** 2))

  @staticmethod
  def weighted_sample_no_replace(items: List[Album], weights: List[float]) -> Album:
    probs = np.array(weights) / sum(weights)
    indices = np.random.choice(len(items), size=1, replace=False, p=probs)
    return [items[i] for i in indices][0]

  def sample_by_target_release_date(self, artist_ids: List[str], num: int, max_iter: int=1000) -> Set[Track]:
    releases: List[Album] = [
      release for artist_id in artist_ids
      for release in self.sp.get_releases(artist_id) or [] if not self.config.core_only or self.is_core_release(release, artist_id)
    ]
    weights: List[float] = [
      self.compute_weight(self.parse_release_date_flexible(r.release_date))
      for r in releases
    ]

    if not releases:
      return set()

    sampled_tracks = set()
    while len(sampled_tracks) < num and max_iter > 0:
      release = self.weighted_sample_no_replace(releases, weights)
      tracks = self.sp.get_album_tracks(release.id) or []
      if tracks:
        track = random.choice(tracks)
        sampled_tracks.add(track)
      max_iter -= 1

    return sampled_tracks

  def sample_multiple_per_artist(self, artist_ids: List[str], num: int) -> Set[Track]:
    return self.sample_by_target_release_date(artist_ids, num=num)

  def sample_evenly_across_artists(self, artist_ids: List[str], num: int) -> Set[Track]:
    return self.sample_by_target_release_date(artist_ids, num=num)

SAMPLERS = {
  "top_songs": TopSongsSampler,
  "random_release": RandomReleaseSongSampler,
  "album_cluster": AlbumClusterSampler,
  "full_track_pool": FullTrackPoolSampler,
  "nearest_release_date": NearestReleaseDateSampler,
  "combined": CombinedSongSampler
}

SamplerConfigUnion = Union[
  TopSongsConfig,
  RandomReleaseConfig,
  AlbumClusterConfig,
  FullTrackPoolConfig,
  NearestReleaseDateConfig
]