class PlaylistManager {
  constructor(session) {
    this.session = session;
    this.container = document.getElementById("playlist-container");
    this.artistPanel = document.getElementById("artist-panel");
    this.albumPanel = document.getElementById("album-panel");
        this.trackList = document.createElement('ul');
    this.container.appendChild(this.trackList);
    this.current_state();
  }

  createPlaylistUI(data) {
    const wrapper = document.createElement('div');

    if (!data) {
      const nameInput = document.createElement('input');
      nameInput.className = "playlist-name";
      nameInput.placeholder = "Playlist name";
      wrapper.appendChild(nameInput);

      const trackCountInput = document.createElement('input');
      trackCountInput.className = "playlist-tracks";
      trackCountInput.placeholder = "Number of tracks";
      trackCountInput.type = "number";
      trackCountInput.value = "10";
      wrapper.appendChild(trackCountInput);

      const createButton = document.createElement('button');
      createButton.textContent = "create";
      createButton.onclick = async () => {
        const res = await fetch('/api/playlist/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: nameInput.value, length: Number(trackCountInput.value) })
        });
        const playlist_data = await res.json();
        this.render(playlist_data);
      };

      wrapper.appendChild(createButton);
    } else {
      const playlistName = document.createElement('h1');
      playlistName.className = "playlist-name";
      playlistName.innerText = data.name;
      wrapper.appendChild(playlistName);

      const desc = document.createElement("p");
      desc.textContent = data.description;
      wrapper.appendChild(desc);

      const updateButton = document.createElement('button');
      updateButton.textContent = "update";
      updateButton.onclick = async () => {
        const res = await fetch('/api/playlist/update', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        const playlist_data = await res.json();
        this.render(playlist_data);
      };

      wrapper.appendChild(updateButton);
    }

    this.container.appendChild(wrapper);
    return wrapper;
  }

  current_state() {
    fetch('/api/playlist/current')
      .then(res => res.json())
      .then(data => this.render(data))
      .catch(err => console.error('Session fetch failed:', err));
  }

  formatDuration(ms) {
    const totalSec = Math.floor(ms / 1000);
    const min = Math.floor(totalSec / 60);
    const sec = totalSec % 60;
    return `${min}:${sec.toString().padStart(2, '0')}`;
  }

  render(data) {
    this.container.innerHTML = "";
    this.data = data;


    const ui = this.createPlaylistUI(data);
    this.container.appendChild(ui);

    if (!data || !data.tracks) return;

    let {tracks, albums, artists} = data;

    const trackList = document.createElement("div");
    trackList.style.display = "flex";
    trackList.style.flexDirection = "column";
    trackList.style.gap = "12px";

    tracks.forEach(track => {
      const album = albums[track.album_id];
      const artistLinks = track.artist_ids.map(id => {
        const name = artists[id]?.name || "Unknown";
        return `<a href="artist-panel" class="artist-link track-artist" data-id="${id}" style="color:blue;text-decoration:underline">${name}</a>`;
      }).join(", ");
      const albumCover = album.images[2]?.url || "";
      const albumName = `<a href="album-panel" class="album-link" data-id="${track.album_id}" style="color:blue;text-decoration:underline">${album.name}</a>`;

      const item = document.createElement("div");
      item.className = "track-item";

      const img = document.createElement("img");
      img.className = "track-column";
      img.src = albumCover;
      img.alt = "album cover";
      img.width = 64;
      img.height = 64;

      const track_info = document.createElement("div");
      track_info.className = "track-column";
      track_info.innerHTML = `
        <h4 class="track-item-name">${track.name}</h4>
        <div>${artistLinks}</div>
      `;

      const album_info = document.createElement("div");
      album_info.className = "track-column";
      album_info.innerHTML = `${albumName}`;

      const duration = document.createElement("div");
      duration.className = "track-column";
      duration.innerHTML = `
        <div>${this.formatDuration(track.duration)}</div>
      `;


      item.appendChild(img);
      item.appendChild(track_info);
      item.appendChild(album_info);
      item.appendChild(duration);
      trackList.appendChild(item);
    });

    this.container.appendChild(trackList);

    // Bind link click handlers
    this.container.querySelectorAll('.artist-link').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        this.showArtistInfo(el.dataset.id);
      });
    });

    this.container.querySelectorAll('.album-link').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        this.showAlbumInfo(el.dataset.id);
      });
    });
  }

  showArtistInfo(artistId) {
    const artist = this.data.artists[artistId];
    if (!artist) return;

    this.artistPanel.innerHTML = `
      <h3>${artist.name}</h3>
      ${artist.images[0] ? `<img src="${artist.images[0].url}" width="200"/>` : ""}
      <p><strong>Genres:</strong> ${artist.genres.join(", ") || "N/A"}</p>
      <p><strong>Popularity:</strong> ${artist.popularity ?? "N/A"}</p>
    `;
    this.artistPanel.scrollIntoView({ behavior: "smooth" });
  }

  showAlbumInfo(albumId) {
    const album = this.data.albums[albumId];
    if (!album) return;

    this.albumPanel.innerHTML = `
      <h3>${album.name}</h3>
      ${album.images[0] ? `<img src="${album.images[0].url}" width="200"/>` : ""}
      <p><strong>Release Date:</strong> ${album.release_date}</p>
      <p><strong>Total Tracks:</strong> ${album.total_tracks}</p>
      <p><strong>Type:</strong> ${album.type}</p>
    `;
    this.albumPanel.scrollIntoView({ behavior: "smooth" });
  }
}

let pl_manager = new PlaylistManager(session);
