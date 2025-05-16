from typing import Set, Dict, Optional, Literal, List
from pydantic import BaseModel, Field

from src.models.ArtistHandler import ArtistHandler
from src.models.ObjectSampling import SamplingStrategyType, FilterTypes
from src.models.PlaylistEditor import PlaylistEditor
from src.models.SongSampler import SongSamplerConfig, SAMPLERS
from src.core.GenreGraph import GenreGraph
from src.core.SpotifyCache import Track


class SampledArtists(BaseModel):
  filter: Optional[FilterTypes] = None
  sampler: Optional[SamplingStrategyType] = None
  sampled: Set[int] = Field(default_factory=set)


class SampledTracks(BaseModel):
  sampler: Optional[SongSamplerConfig] = None
  sampled: Set[Track] = Field(default_factory=set)


class UserGenre(BaseModel):
  id: int
  name: str
  selected: bool = False
  expanded: bool = False
  artists: Optional[SampledArtists] = None
  tracks: Optional[SampledTracks] = None


class PlaylistFactory(BaseModel):
  genres: Dict[int, UserGenre] = Field(default_factory=dict)
  playlist: PlaylistEditor = Field(default_factory=PlaylistEditor)

  def selected_genres(self) -> List[int]:
    return [g.id for g in self.genres.values() if g.selected]

  def expanded_genres(self) -> List[int]:
    return [g.id for g in self.genres.values() if g.expanded]

  def genre_ids(self) -> List[int]:
    return [g.id for g in self.genres.values()]

  def add_genre(self, genre_id: int):
    g = GenreGraph().get_genre(genre_id)
    self.genres[genre_id] = UserGenre(id=genre_id, name=g["name"])

  def remove_genre(self, genre_id: int):
    if genre_id in self.genres:
      del self.genres[genre_id]

  def has(self, genre_id: int) -> bool:
    return genre_id in  self.genres

  def toggle_genre(self, genre_id: int):
    if genre_id in self.genres:
      self.remove_genre(genre_id)
    else:
      self.add_genre(genre_id)

  def toggle_expand(self, genre_id: int):
    self.genres[genre_id].expanded = not self.genres[genre_id].expanded

  def toggle_select(self, genre_id: int):
    self.genres[genre_id].selected = not self.genres[genre_id].selected

  def collapse_all(self):
    for genre in self.genres.values():
      genre.expanded = False

  def clear(self):
    self.genres.clear()

  def remove_unexplored(self):
    to_remove = [
      g_id for g_id, genre in self.genres.items()
      if not genre.expanded and not genre.selected and genre.artists is None and genre.tracks is None
    ]
    for g_id in to_remove:
      self.remove_genre(g_id)

  def reset(self, genre_id: int, mode: Literal["all", "artists", "tracks"]):
    if mode == "all":
      self.add_genre(genre_id)
    elif mode == "artists":
      self.genres[genre_id].artists = None
    elif mode == "tracks":
      self.genres[genre_id].tracks = None

  def sample_artists(self, genre_id: int, sampler: SamplingStrategyType, filter_cls: Optional[FilterTypes] = None, limit: int=20, reset: bool=True):
    if genre_id not in self.genres:
      self.add_genre(genre_id)

    genre = self.genres[genre_id]

    if genre.artists is None:
      genre.artists = SampledArtists(filter=filter_cls, sampler=sampler)
    else:
      genre.artists.filter = filter_cls
      genre.artists.sampler = sampler

    if reset:
      genre.artists.sampled.clear()

    pool = ArtistHandler().get_pool(genre_id)
    artists = filter_cls(pool.artists) if filter_cls else pool.artists

    for _ in range(100):
      if len(genre.artists.sampled) >= limit:
        break
      artist = sampler.apply(artists)
      genre.artists.sampled.add(artist.id)

  def sampled_artists(self, genre_id: Optional[int] = None) -> Dict[int, list]:
    if genre_id and self.genres[genre_id].selected:
      return {genre_id: list(self.genres[genre_id].artists.sampled)}
    return {genre.id: list(genre.artists.sampled) for genre in self.genres.values() if genre.selected and genre.artists}

  def sample_tracks(self, genre_id: int, sampler_config: SongSamplerConfig, limit: int=20, reset: bool=True):
    genre: UserGenre = self.genres[genre_id]

    if genre.tracks is None:
      genre.tracks = SampledTracks(sampler=sampler_config)
    else:
      genre.tracks.sampler = sampler_config
    pool = ArtistHandler().get_pool(genre_id)

    artist_ids = [a.spotify_id for a in pool.artists if a.id in self.genres[genre_id].artists.sampled]
    sampler = SAMPLERS[sampler_config.type](config=sampler_config)
    tracks = sampler.sample(artist_ids, limit)

    if reset:
      genre.tracks.sampled.clear()

    genre.tracks.sampled.update(tracks)

  def sampled_tracks(self, genre_id: Optional[int] = None) -> Set[Track]:
    sampled_genres = [genre for genre in self.genres.values() if genre.selected and genre.tracks]
    if genre_id and self.genres[genre_id].selected:
      return set(track for track in self.genres[genre_id].tracks.sampled)
    return set(track for genre in sampled_genres for track in genre.tracks.sampled)

  def rebuild_playlist(self):
    trackset = set(self.playlist.tracks)
    sampled_tracks = self.sampled_tracks()

    self.playlist.remove_tracks(trackset - sampled_tracks)
    self.playlist.add_tracks(sampled_tracks - trackset)

  def reorder_playlist(self):
    pass # TODO

  def update_playlist(self):
    self.rebuild_playlist()
    self.reorder_playlist()