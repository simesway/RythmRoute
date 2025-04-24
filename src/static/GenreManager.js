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
    this.container = document.getElementById('card-container');
    this.genres = new Map(); // id → Genre
    this.selected = [];
    this.expanded = [];

    this.genre_cards = new Map();

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
    return this.selected.includes(Number(genre_id));
  }

  isExpanded(genre_id) {
    return this.expanded.includes(Number(genre_id));
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
        this.genres.delete(id);
      }
    }

    for (const id of this.selected) {
      let card = this.genre_cards.get(String(id));
      if (card) {
      } else {
        let genre = this.get(id);
        this.genre_cards.set(String(id), new GenreCard(this.session, genre, "card-container"));
      }
    }
  }

  toggleExpandGenre(id) {
    if (!this.has(id)) return;
    let genre = this.get(id);
    let action= genre.hasSubgenre ? "expand" : "highlight";
    this.session.updateOnServer({action: action, id: genre.id }, '/api/graph/update');
  }

  toggleSelectGenre(id) {
    if (!this.has(id)) return;
    let genre = this.get(id);
    let action = genre.isSelectable ? "select" : "highlight";
    this.session.updateOnServer({action: action, id: genre.id }, '/api/graph/update');

    const card = this.genre_cards.get(String(id));
    if (card) {
      card.destroy();
      this.genre_cards.delete(id);
    }
  }

}


const genre_manager = new GenreManager();