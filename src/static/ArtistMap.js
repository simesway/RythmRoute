class Artist {
  constructor(data) {
    this.id = data.id;
    this.spotify_id = data.spotify_id;
    this.name = data.name;
    this.popularity = data.popularity;
    this.bouncyness = data.bouncyness;
    this.organicness = data.organicness;
  }

  draw_dot(p, x, y, inner_fill, outer_fill) {
    let R = 8 + this.popularity/5;
    let r = R * 0.5;
    p.noStroke()
    p.fill(outer_fill);
    p.circle(x, y, R);
    p.fill(inner_fill);
    p.circle(x, y, r);
  }

  draw(p, x, y, inner_fill, outer_fill) {
    let text_size = 12 + this.popularity/5;
    p.strokeWeight(text_size / 4);
    p.stroke(outer_fill);
    p.fill(inner_fill);
    p.textAlign(p.CENTER, p.CENTER);
    p.textSize(text_size);
    p.text(this.name, x, y);
  }
}


class ArtistPool  {
  constructor(pool_data, sampled) {
    this.genre_id = pool_data.genre_id;
    this.name = pool_data.name;
    this.bouncyness = pool_data.bouncyness;
    this.organicness = pool_data.organicness;
    this.artists = [];
    this.sampled = sampled ?? [];

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
    console.log("ArtistMap init");
    this.p = p;
    this.session = session;
    this.genres = genre_manager;

    this.pools = [];
    this.alpha = 0.2;

    this.electric_color = p.color(255);
    this.organic_color = p.color(0, 255, 0);
    this.atmospheric_color = p.color(0, 0, 120);
    this.bouncy_color = p.color('#FE9000');

    this.draw_dot = false;

    this.session.subscribe(state => this.update_graph_from_session(state));
    //this.session.fetchState();
  }

  update_graph_from_session(data) {
    const { pools, sampled } = data.artists;
    if (!pools?.length) return;

    this.pools = pools.map(pool => new ArtistPool(pool, sampled[pool.genre_id]));
    this.updateMinMax();
    this.render_sampled_artists(data);
  }

  updateMinMax() {
    let visiblePools = this.pools.filter(pool => {
      const card = document.getElementById(`genre:${pool.genre_id}`);
      return card?.querySelector(".card-content")?.style.display !== "none";
    });

    if (!visiblePools.length) {
      this.b_min = this.b_max = this.o_min = this.o_max = 0;
      return;
    }

    this.b_min = Math.min(...visiblePools.map(p => p.bouncyness));
    this.b_max = Math.max(...visiblePools.map(p => p.bouncyness));
    this.o_min = Math.min(...visiblePools.map(p => p.organicness));
    this.o_max = Math.max(...visiblePools.map(p => p.organicness));
  }

  render_sampled_artists(data) {
    for (let pool of this.pools) {
      const sampled_artists = data.factory.genres[pool.genre_id]?.artists?.sampled || [];
      const panel = document.getElementById(`${pool.genre_id}-sampled-artists`);
      if (!panel) continue;

      panel.innerHTML = "";
      const filtered = pool.artists
        .filter(a => sampled_artists.includes(Number(a.id)))
        .sort((a, b) => a.name.localeCompare(b.name));

      for (let artist of filtered) {
        const el = document.createElement("div");
        el.textContent = artist.name;
        panel.appendChild(el);
      }
    }
  }

  scale(v, inMin, inMax, outMin, outMax) {
    if (inMax === inMin) return outMin;
    return ((v - inMin) * (outMax - outMin)) / (inMax - inMin) + outMin;
  }

  draw_legend() {
    const { width: w, height: h } = this.p;
    const pad = 110;
    this.p.textAlign(this.p.CENTER, this.p.CENTER);
    this.p.textSize(30);
    this.p.strokeWeight(3);
    this.p.stroke(0);
    this.p.textStyle(this.p.BOLD);

    this.p.fill(this.electric_color); this.p.text("electric", w/2, pad);
    this.p.fill(this.organic_color); this.p.text("organic", w/2, h - pad);
    this.p.fill(this.atmospheric_color); this.p.text("atmospheric", pad, h/2);
    this.p.fill(this.bouncy_color); this.p.text("bouncy", w - pad, h/2);
    this.p.textStyle(this.p.NORMAL)
  }

  draw() {
    this.draw_legend();
    if (!this.pools.length) return;

    this.updateMinMax();

    const pad = 64;
    const w = this.p.width - 2 * pad;
    const h = this.p.height - 2 * pad;
    const alpha = this.alpha;
    const b_min = this.b_min - alpha / 2;
    const b_max = this.b_max + alpha / 2;
    const o_min = this.o_min - alpha / 2;
    const o_max = this.o_max + alpha / 2;

    this.p.stroke(0); this.p.strokeWeight(1); this.p.noFill();
    this.p.rect(pad, pad, w, h);

    this.p.strokeWeight(3);
    this.p.line(this.scale(0, b_min, b_max, 0, this.p.width), this.scale(0.5, o_min, o_max, 0, this.p.height),
                this.scale(1, b_min, b_max, 0, this.p.width), this.scale(0.5, o_min, o_max, 0, this.p.height));
    this.p.line(this.scale(0.5, b_min, b_max, 0, this.p.width), this.scale(0, o_min, o_max, 0, this.p.height),
                this.scale(0.5, b_min, b_max, 0, this.p.width), this.scale(1, o_min, o_max, 0, this.p.height));

    let hovered = null, hovered_pool = null;

    for (let pool of this.pools) {
      const card = document.getElementById(`genre:${pool.genre_id}`);
      if (!card?.querySelector(".card-content") || card.querySelector(".card-content").style.display === "none") continue;

      for (let artist of pool.artists) {
        if (!pool.sampled.includes(Number(artist.id))){
          const adj_b = pool.bouncyness + alpha * (artist.bouncyness - 0.5);
          const adj_o = pool.organicness + alpha * (artist.organicness - 0.5);
          const x = this.scale(adj_b, b_min, b_max, 0, w) + pad;
          const y = this.scale(adj_o, o_min, o_max, 0, h) + pad;
          const d = this.p.dist(this.p.mouseX, this.p.mouseY, x, y);
          const R = 8 + artist.popularity / 5;
          if (d < R) [hovered, hovered_pool] = [artist, pool];
          const color_b = this.p.lerpColor(this.atmospheric_color, this.bouncy_color, adj_b);
          const color_o = this.p.lerpColor(this.electric_color, this.organic_color, adj_o);
          this.draw_dot ? artist.draw_dot(this.p, x, y, color_o, color_b) : artist.draw(this.p, x, y, color_o, color_b);
        }
      }
      for (let artist of pool.artists) {
        if (pool.sampled.includes(Number(artist.id))){
          const adj_b = pool.bouncyness + alpha * (artist.bouncyness - 0.5);
          const adj_o = pool.organicness + alpha * (artist.organicness - 0.5);
          const x = this.scale(adj_b, b_min, b_max, 0, w) + pad;
          const y = this.scale(adj_o, o_min, o_max, 0, h) + pad;
          const d = this.p.dist(this.p.mouseX, this.p.mouseY, x, y);
          const R = 8 + artist.popularity / 5;
          if (d < R) [hovered, hovered_pool] = [artist, pool];
          const color_b = this.p.color(255,0,0);
          const color_o = this.p.color(255);
          this.draw_dot ? artist.draw_dot(this.p, x, y, color_o, color_b) : artist.draw(this.p, x, y, color_o, color_b);
        }
      }
    }

    for (let pool of this.pools) {
      const x = this.scale(pool.bouncyness, b_min, b_max, 0, w) + pad;
      const y = this.scale(pool.organicness, o_min, o_max, 0, h) + pad;
      pool.draw(this.p, x, y);
    }

    if (hovered) {
      const adj_b = hovered_pool.bouncyness + alpha * (hovered.bouncyness - 0.5);
      const adj_o = hovered_pool.organicness + alpha * (hovered.organicness - 0.5);
      const x = this.scale(adj_b, b_min, b_max, 0, w) + pad;
      const y = this.scale(adj_o, o_min, o_max, 0, h) + pad;
      const color_b = this.p.lerpColor(this.atmospheric_color, this.bouncy_color, hovered_pool.bouncyness);
      const color_o = this.p.lerpColor(this.electric_color, this.organic_color, hovered_pool.organicness);
      this.draw_dot ? hovered.draw_dot(this.p, x, y, color_o, color_b) : hovered.draw(this.p, x, y, color_o, color_b);
    }
  }

  keyPressed() {
    if (this.p.keyCode === this.p.RIGHT_ARROW) this.alpha = this.p.lerp(this.alpha, 0.5, 0.05);
    if (this.p.keyCode === this.p.LEFT_ARROW) this.alpha = this.p.lerp(this.alpha, 0.001, 0.05);
    if (this.p.key === "d") this.draw_dot = !this.draw_dot;
  }
}


export default ArtistMap;