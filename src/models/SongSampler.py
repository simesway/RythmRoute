from abc import ABC, abstractmethod
from src.services.SpotifyCache import Album, Track, SpotifyCache, Release
from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime
import numpy as np
import math
import random

NON_CORE_KEYWORDS = [
  "remix", "live", "deluxe", "instrumental",
  "karaoke", "acoustic", "demo", "commentary",
  "bonus", "edit", "version", "reissue",
  "mix", "intro", "outro", "skit", "prolog",
  "interlude", "revisited"
]

class SongSampler(ABC):
  def __init__(self):
    self.sp = SpotifyCache()

  @staticmethod
  def is_core_release(release: Release):
    name = release.name.lower()
    return not any(keyword in name for keyword in NON_CORE_KEYWORDS)

  def sample_songs(self, artist_ids: List[str], num: int = 5) -> Set[Track]:
    if not artist_ids or num <= 0:
      return set()

    if num < len(artist_ids):
      return self.sample_evenly_across_artists(artist_ids, num)
    else:
      return self.sample_multiple_per_artist(artist_ids, num)

  @abstractmethod
  def sample_evenly_across_artists(self, artist_ids: List[str], num: int) -> Set[Track]:
    return set()

  @abstractmethod
  def sample_multiple_per_artist(self, artist_ids: List[str], num: int) -> Set[Track]:
    return set()


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


class AlbumClusterSampler(SongSampler):
  def __init__(self, exclude_types: List[str] = None, core_only: bool = False):
    super().__init__()
    self.exclude_types = exclude_types or []
    self.core_only = core_only

  @staticmethod
  def cluster_releases(releases: List[Album]) -> Dict[str, List[Album]]:
    clusters = defaultdict(list)
    for release in releases:
        clusters[release.type].append(release)
    return dict(clusters)

  def sample_from_release_clusters(self, artist_ids: List[str], num: int = 5, max_iter: int = 1000) -> Set[Track]:
    releases = [
      release for artist_id in artist_ids
      for release in self.sp.get_releases(artist_id) or [] if not self.core_only or self.is_core_release(release)
    ]
    if not releases:
      return set()

    clusters = self.cluster_releases(releases)
    filtered = {k: v for k, v in clusters.items() if k not in self.exclude_types}
    if not filtered:
      return set()

    sampled_tracks = set()
    while len(sampled_tracks) < num and max_iter > 0:
      release_type = random.choice(list(filtered))
      release = random.choice(filtered[release_type])
      tracks = self.sp.get_album_tracks(release.id) or []
      tracks = [track for track in tracks if not self.core_only or self.is_core_release(track)]
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


class FullTrackPoolSampler(SongSampler):
  def __init__(self, core_only: bool = False):
    super().__init__()
    self.core_only = core_only

  def sample_from_full_track_pool(self, artist_ids: List[str], num: int) -> Set[Track]:
    releases = [
      release for artist_id in artist_ids
      for release in self.sp.get_releases(artist_id) or [] if not self.core_only or self.is_core_release(release)
    ]
    tracks = set(
      track for release in releases for track in self.sp.get_album_tracks(release.id)
      if not self.core_only or self.is_core_release(track)
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


class NearestReleaseDateSampler(SongSampler):
  def __init__(self, target_date: datetime, sigma_days: float=180., core_only: bool = False):
    super().__init__()
    self.target_date = target_date
    self.sigma_days = sigma_days
    self.core_only = core_only

  @staticmethod
  def parse_release_date_flexible(release_date: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
      try:
        return datetime.strptime(release_date, fmt)
      except ValueError:
        continue
    raise ValueError(f"Unknown release_date format: {release_date}")

  def compute_weight(self, release_date: datetime) -> float:
    delta_days = abs((release_date - self.target_date).days)
    return math.exp(- (delta_days ** 2) / (2 * self.sigma_days ** 2))

  @staticmethod
  def weighted_sample_no_replace(items: List[Album], weights: List[float]) -> Album:
    probs = np.array(weights) / sum(weights)
    indices = np.random.choice(len(items), size=1, replace=False, p=probs)
    return [items[i] for i in indices][0]

  def sample_by_target_release_date(self, artist_ids: List[str], num: int, max_iter: int=1000) -> Set[Track]:
    releases: List[Album] = [
      release for artist_id in artist_ids
      for release in self.sp.get_releases(artist_id) or [] if not self.core_only or self.is_core_release(release)
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