import logging
from pydantic import BaseModel, PrivateAttr, Field
from typing import List, Optional, Set, Union
from spotipy import Spotify

from src.core.SpotifyCache import Track, SpotifyCache


class PlaylistEditor(BaseModel):
  """A class for creating and managing Spotify playlists via the Spotify API."""
  id: Optional[str] = None
  name: Optional[str] = None
  description: Optional[str] = None
  public: bool = False
  tracks: List[Track] = Field(default_factory=list)

  _spotify: Optional[Spotify] = PrivateAttr(default=None)

  def set_spotify(self, sp: Spotify):
    """Attach a Spotify client to this editor."""
    self._spotify = sp
    return self

  def _check_session(self, required_id: bool=True):
    """Ensure the Spotify client and playlist ID are set."""
    if self._spotify is None:
        raise ValueError("Spotify session not set.")
    if required_id and self.id is None:
        self.create()

  def create(self):
    """Create a new Spotify playlist and store its ID."""
    self._check_session(required_id=False)
    response = self._spotify.user_playlist_create(
      user=self._spotify.current_user()["id"],
      name=self.name or "New Playlist",
      description=self.description or "",
      public=self.public
    )
    self.id = response['id']
    logging.info(f"Created Playlist: {self.id}")

  def add_tracks(self, tracks: Union[Set[Track], List[Track]]):
    """Add tracks to the playlist."""
    if tracks is None:
      return
    self._check_session()
    track_ids = [t.id for t in tracks]
    if track_ids:
      logging.info(f"Adding Tracks: num={len(track_ids)} id={self.id}")
      self._spotify.playlist_add_items(self.id, [t.id for t in tracks])
      self.tracks.extend(tracks)

  def remove_tracks(self, tracks: Union[Set[Track], List[Track]]):
    """Remove tracks from the playlist."""
    if len(tracks) == 0:
      return
    self._check_session()
    track_ids = [t.id for t in tracks]
    if track_ids:
      logging.info(f"Removing Tracks: num={len(track_ids)} id={self.id}")
      self._spotify.playlist_remove_all_occurrences_of_items(self.id, track_ids)
      self.tracks = [t for t in self.tracks if t.id not in track_ids]

  def update_details(self, name: Optional[str] = None, description: Optional[str] = None, public: Optional[bool] = None):
    """Update playlist details: Name, description and publicity."""
    self._check_session()
    self._spotify.playlist_change_details(
      playlist_id=self.id,
      name=name or self.name,
      description=description or self.description,
      public=public or self.public
    )
    self.name = name or self.name
    self.description = description or self.description
    self.public = public or self.public
    logging.info(f"Updated Playlist Details: id={self.id}")

  def to_frontend(self):
    """Prepare playlist data for frontend use."""
    cache = SpotifyCache()
    album_ids = set(t.album_id for t in self.tracks)
    artist_ids = set(artist_id for t in self.tracks for artist_id in t.artist_ids)
    return {
      "name": self.name,
      "description": self.description,
      "tracks": self.tracks,
      "albums": {a.id: a for a in cache.get_albums(list(album_ids))},
      "artists": {a.id: a for a in cache.get_artists(list(artist_ids))}
    }
