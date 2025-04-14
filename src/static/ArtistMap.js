let rel_color = "#016FB9"

class Artist {
  constructor(data) {
    this.id = data.id;
    this.spotify_id = data.spotify_id;
    this.name = data.name;
    this.popularity = data.popularity;
    this.bouncyness = data.bouncyness;
    this.organicness = data.organicness;
  }

  draw_dot(p, x, y, fill) {

    p.strokeWeight(3);
    p.stroke(0);
    p.fill(fill);
    p.circle(x, y, 5 + this.popularity/5);
  }

  draw(p, x, y) {
    p.strokeWeight(3);
    p.stroke(0);
    p.fill(255);
    p.textAlign(p.CENTER, p.CENTER);
    p.textSize(10 + this.popularity/10);
    p.text(this.name, x, y);
  }
}


class ArtistPool  {
  constructor(pool_data) {
    this.genre_id = pool_data.genre_id;
    this.name = pool_data.name;
    this.bouncyness = pool_data.bouncyness;
    this.organicness = pool_data.organicness;
    this.artists = [];

    for (let artist_data of pool_data.artists) {
      this.artists.push(new Artist(artist_data));
    }
  }


  draw(p, x, y) {
    p.strokeWeight(5);
    p.stroke(255);
    p.fill(0);
    p.textAlign(p.CENTER, p.CENTER);
    p.textSize(20);
    p.text(this.name, x, y);
  }
}


class ArtistMap {
  constructor(p) {
    console.log("ArtistMap init")
    this.p = p;
    this.session = session;

    this.pools = []
    this.b_min = 0;
    this.b_max = 1;
    this.o_min = 0;
    this.o_max = 1;

    this.alpha = 0.1;

    this.draw_dot = false;

    this.session.subscribe((state) => {
      this.update_graph_from_session(state.artists);
    });
    this.session.fetchState()
  }

  update_graph_from_session(data) {
    const { pools: pools, selected: selected } = data;

    if (!pools || pools.length === 0) {
      return;
    }

    this.pools = [];

    for (let pool of pools) {
      this.pools.push(new ArtistPool(pool));
    }

    let b_values = this.pools.map(pool => pool.bouncyness);
    let o_values = this.pools.map(pool => pool.organicness);

    this.b_min = Math.min(...b_values);
    this.b_max = Math.max(...b_values);

    this.o_min = Math.min(...o_values);
    this.o_max = Math.max(...o_values);

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

  normalize(value, min, max) {
    if (max === min) return 0; // or 1, depending on your use case
    return (value - min) / (max - min);
  }

  scale(value, inMin, inMax, outMin, outMax) {
    return ((value - inMin) * (outMax - outMin)) / (inMax - inMin) + outMin;
  }

  draw() {
    this.draw_legend()
    if (!this.pools || this.pools.length === 0)  return;

    let pad = 64;
    let w = this.p.width - 2 * pad;
    let h = this.p.height - 2 * pad;

    let alpha = this.alpha;
    let b_min = this.b_min - alpha/2;
    let b_max = this.b_max + alpha/2;
    let o_min = this.o_min - alpha/2;
    let o_max = this.o_max + alpha/2;

    //this.p.rect(pad, pad, w, h);

    let x1 = this.scale(0, b_min, b_max, 0, w) + pad;
    let xh = this.scale(0.5, b_min, b_max, 0, w) + pad;
    let x2 = this.scale(1, b_min, b_max, 0, w) + pad;
    let y1 = this.scale(0, o_min, o_max, 0, h) + pad;
    let yh = this.scale(0.5, o_min, o_max, 0, h) + pad;
    let y2 = this.scale(1, o_min, o_max, 0, h) + pad;

    this.p.strokeWeight(3);
    this.p.stroke(0);
    this.p.line(x1, yh, x2, yh);
    this.p.line(xh, y1, xh, y2);



    for (let pool of this.pools) {
      for (let artist of pool.artists) {
        let adj_bouncyness = pool.bouncyness + alpha * (artist.bouncyness - 0.5);
        let adj_organicness = pool.organicness + alpha * (artist.organicness - 0.5);
        let artist_x = this.scale(adj_bouncyness, b_min, b_max, 0, w) + pad;
        let artist_y = this.scale(adj_organicness, o_min, o_max, 0, h) + pad;
        if (this.draw_dot) {
          artist.draw_dot(this.p, artist_x, artist_y, pool.genre_id);
        } else {
          artist.draw(this.p, artist_x, artist_y, pool.genre_id);
        }

      }
    }
    for (let pool of this.pools) {
      let pool_x = this.scale(pool.bouncyness, b_min, b_max, 0, w) + pad;
      let pool_y = this.scale(pool.organicness, o_min, o_max, 0, h) + pad;
      pool.draw(this.p, pool_x, pool_y);
    }
  }

  keyPressed() {
    let keyCode = this.p.keyCode;
    let key = this.p.key;
    if (keyCode === this.p.RIGHT_ARROW) { // Check if the "X" key is pressed
      this.alpha = this.p.lerp(this.alpha, 0.5, 0.05);
    }
    if (keyCode === this.p.LEFT_ARROW) { // Check if the "X" key is pressed
      this.alpha = this.p.lerp(this.alpha, 0.001, 0.05);
    }
    if (key === "d") { // Check if the "X" key is pressed
      this.draw_dot = !this.draw_dot;
    }
  }
}

export default ArtistMap;