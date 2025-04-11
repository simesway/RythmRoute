let rel_color = "#016FB9"

class Artist {
  constructor(p, id, spotify_id, name, popularity, x, y) {
    this.p = p;
    this.id = id;
    this.spotify_id = spotify_id;
    this.name = name;
    this.popularity = popularity;
    this.x = x;
    this.y = y;
    this.r = popularity;

    this.target_x = x;
    this.target_y = y;

    this.selected = false;
    this.expanded = false;
    this.isExpandable = false;
  }

  set_target(x, y) {
    this.target_x = x;
    this.target_y = y;
  }

  update(rate) {
    this.x = this.p.lerp(this.x, this.target_x, rate)
    this.y = this.p.lerp(this.y, this.target_y, rate)
  }

  isHovered(px, py, w, h, pad) {
    const gx = this.x * w + pad;
    const gy = this.y * h + pad;
    return this.p.dist(px, py, gx, gy) <= this.r * 2;
  }

  draw(pad, w, h, highlight=false) {
    let x = this.x * w + pad;
    let y = this.y * h + pad;
    let r = this.isExpandable ? 24 : 13;


    this.p.strokeWeight(5);
    this.p.stroke(0)
    this.p.fill(255);
    this.p.textAlign(this.p.CENTER, this.p.CENTER);
    this.p.textSize(10);
    this.p.text(this.name, x, y);
  }
}


class ArtistMap {
  constructor(p) {
    console.log("ArtistMap init")
    this.p = p;
    this.session = session;
    this.artists = new Map();

    this.selected = [];
    this.expanded = [];
    this.highlight = null;

    this.drawQueue = [];

    this.session.subscribe((state) => {
      this.update_graph_from_session(state.artists);
    });
    this.session.fetchState()
  }

  update(rate) {
    for (let artist of this.artists.values()) {
      artist.update(rate)
    }
  }

  update_highlight(id, name, description) {
    let artist;
    if (id) {
      artist = this.genres.get(id);
    }
    this.highlight = id;
    name = id ? artist.name : "Select an Artist";

    document.getElementById('artist-name').innerText = name;

  }

  update_graph_from_session(data) {
    console.log(data)
    const { artists: artists, layout: layout, state: state } = data;
    const { selected: selected} = state;

    console.log(artists)

    artists.forEach(artist => {
      let isSelected = selected.includes(artist.spotify_id);
      let spotify_id = artist.spotify_id

      if (this.artists.has(spotify_id)) {
        let existing = this.artists.get(spotify_id);
        let pos = layout[spotify_id];
        existing.set_target(pos.x, pos.y);
        existing.selected = isSelected;

      } else {
        let pos = layout[spotify_id];
        let x = 0.5;
        let y = 0.5;

        let a = new Artist(this.p, artist.id, artist.spotify_id, artist.name, artist.popularity, x, y);
        a.set_target(pos.x, pos.y);
        a.selected = isSelected;
        this.artists.set(artist.spotify_id, a);
        this.drawQueue.push(artist.spotify_id);
      }
    });

    const validIds = new Set(artists.map(a => a.spotify_id));
    for (let id of this.artists.keys()) {
      if (!validIds.has(id)) {
          this.artists.delete(id);
          let index = this.drawQueue.indexOf(id);
          if (index !== -1) this.drawQueue.splice(index, 1);
      }
    }

    console.log(this.artists)

  }

  draw_legend() {
    let w = this.p.width;
    let h = this.p.height;
    let pad = 100;
    this.p.noStroke()
    this.p.fill(255);
    this.p.textAlign(this.p.CENTER, this.p.CENTER);
    this.p.textSize(30);
    this.p.text("electric", w/2, pad);
    this.p.text("organic", w/2, h-pad);
    this.p.text("atmospheric", pad, h/2);
    this.p.text("bouncy", w-pad, h/2);
  }

  draw() {
    this.draw_legend()
    let pad = 64;
    let w = this.p.width - 2 * pad;
    let h = this.p.height - 2 * pad;

    for (let item of [...this.drawQueue].reverse()) {
      let highlight = false;
      if (this.highlight === item) {
          highlight = true;
      }
      this.artists.get(item).draw(pad, w, h, highlight);
    }
  }

}

export default ArtistMap;