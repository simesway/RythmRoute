from pydantic import BaseModel, PrivateAttr
from typing import List, Optional
from spotipy import Spotify

from src.core.SpotifyCache import Track, SpotifyCache


class PlaylistEditor(BaseModel):
  id: Optional[str] = None
  name: Optional[str] = None
  description: Optional[str] = None
  public: bool = False
  tracks: List[Track] = []

  _spotify: Optional[Spotify] = PrivateAttr(default=None)

  def set_spotify_client(self, sp: Spotify):
    self._spotify = sp

  def _check_session(self):
    if self._spotify is None:
      raise ValueError("Spotify session not set or playlist already exists.")

  def create(self):
    self._check_session()

    response = self._spotify.user_playlist_create(
      user=self._spotify.current_user()["id"],
      name=self.name or "New Playlist",
      description=self.description or "",
      public=self.public
    )
    self.id = response['id']

  def add_tracks(self, tracks: List[Track]):
    self._check_session()
    self._spotify.playlist_add_items(self.id, [t.id for t in tracks])
    self.tracks.extend(tracks)

  def remove_tracks(self, tracks: List[Track]):
    self._check_session()
    track_ids = [t.id for t in tracks]
    self._spotify.playlist_remove_all_occurrences_of_items(self.id, track_ids)
    self.tracks = [t for t in self.tracks if t.id not in track_ids]

  def update_details(self, name: Optional[str] = None, description: Optional[str] = None, public: Optional[bool] = None):
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

  def to_frontend(self):
    album_ids = set(t.album_id for t in self.tracks)
    artist_ids = set(artist_id for t in self.tracks for artist_id in t.artist_ids)
    return {
      "name": self.name,
      "description": self.description,
      "tracks": self.tracks,
      "albums": {album_id: SpotifyCache().get_album(album_id) for album_id in album_ids},
      "artists": {artist_id: SpotifyCache().get_artist(artist_id) for artist_id in artist_ids}
    }
