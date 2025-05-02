from src.services.SpotifyCache import Track, SpotifyCache
from typing import List
import random

class SongSampler:
  def __init__(self):
    self.sp = SpotifyCache()

  def sample_songs(self, artist_ids, samples_per_artist=1) -> List[Track]:
    sampled_tracks = []
    for artist_id in artist_ids:
      tracks = self.sp.get_top_tracks(artist_id)
      if tracks:
        sampled = random.sample(tracks, min(samples_per_artist, len(tracks)))
        sampled_tracks.extend(sampled)
    return sampled_tracks