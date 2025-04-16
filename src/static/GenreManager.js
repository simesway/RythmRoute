class Genre {
  constructor(data) {
    this.id = data.id;
    this.name = data.name;
    this.bouncyness = data.bouncyness ?? null;
    this.organicness = data.organicness ?? null;
    this.hasSubgenre = data.has_subgenre;
    this.isSelectable = data.is_selectable;
  }
}


class GenreManager {
  constructor() {
    //this.container = document.getElementById();
    this.genres = new Map(); // id → Genre

    this.session = session;
    this.session.subscribe((state) => {
      this.update_genres(state.genre_data);
    });
    this.session.fetchState()
  }

  has(genre_id) {
    return this.genres.has(String(genre_id));
  }

  isSelected(genre_id) {
    return this.selected.includes(String(genre_id));
  }

  isExpanded(genre_id) {
    return this.expanded.includes(String(genre_id));
  }

  get(genre_id) {
    return this.genres.get(String(genre_id));
  }

  update_genres(data) {
  const { genres: new_genres, state } = data;
  const { selected, expanded, highlight } = state;

  this.selected = selected;
  this.expanded = expanded;
  this.highlight = highlight;

  const new_ids = new Set(new_genres.map(g => String(g.id)));

  new_genres.forEach(genre => {
    const id = String(genre.id);
    if (!this.genres.has(id)) {
      this.genres.set(id, new Genre(genre));
    }
  });

  for (const id of this.genres.keys()) {
    if (!new_ids.has(id)) {
      this.removeGenre(id);
    }
  }
}

  addGenre(genre) {
    if (this.genres.has(genre.id)) return;
    this.genres.set(genre.id, genre);
    this._renderCard(genre);
  }

  removeGenre(id) {
    id = String(id);
    this.genres.delete(id);
    const card = document.getElementById(id);
    if (card) card.remove();
  }

  _renderCard(genre) {
    const card = document.createElement('div');
    card.className = 'card';
    card.id = genre.id;
    card.innerHTML = `
      <h3>${genre.name}</h3>
      <button onclick="genreManager.removeGenre('${genre.id}')">Remove</button>
    `;
    this.container.appendChild(card);
  }
}


const genre_manager = new GenreManager();