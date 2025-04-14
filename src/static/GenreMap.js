let rel_color = "#016FB9"

class Genre {
  constructor(p, id, name, description, x, y, r) {
    this.p = p;
    this.id = id;
    this.name = name;
    this.description = description;
    this.x = x;
    this.y = y;
    this.r = r;

    this.target_x = x;
    this.target_y = y;

    this.text_bbox;

    this.depth = 8;
    this.selected = false;
    this.expanded = false;
    this.isExpandable = false;
    this.isSelectable = false;
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



    if (highlight) {
      this.p.fill(255, 0, 0);
      this.p.noStroke()
      this.p.circle(x, y, r+10)
    }

    this.p.fill(180);
    this.p.noStroke();

    if (this.isSelectable) {
      this.p.fill(30);
    }
    if (this.selected) {
      this.p.fill("#FF6500");
    }

    if (this.isExpandable) {
      this.p.strokeWeight(5);
      this.p.stroke("#FC6FB9");
    }
    if (this.expanded) {
      this.p.stroke("#016FB9");
    }

    this.p.circle(x, y, r);

    this.p.strokeWeight(5);
    this.p.stroke(0)
    this.p.fill(255);
    this.p.textAlign(this.p.CENTER, this.p.CENTER);
    this.p.textSize(15);
    this.p.text(this.name, x, y - r);
  }
}


class GenreMap {
  constructor(p) {
    this.p = p;
    this.session = session;
    this.genres = new Map();
    this.relationships = [];
    this.radius = 10;

    this.selected = [];
    this.expanded = [];
    this.highlight = null;

    this.drawQueue = [];

    this.session.subscribe((state) => {
      this.update_graph_from_session(state.graph);
    });

    this.session.fetchState();
  }

  update(rate) {
    for (let genre of this.genres.values()) {
      genre.update(rate)
    }
  }

  update_highlight(id, name, description) {
    let genre;
    if (id) {
      genre = this.genres.get(id);
    }
    this.highlight = id;
    name = id ? genre.name : "Choose a Genre";
    description = id ? genre.description : "click on a genre to see information here.";

    document.getElementById('genre-name').innerText = name;
    document.getElementById('genre-description').innerText = description;

  }

  update_graph_from_session(data) {
    const { genres: genres, relationships: relationships, layout: layout, state: state } = data;
    const { selected: selected, expanded: expanded, highlight: highlight} = state;

    genres.forEach(genre => {
      let isSelected = selected.includes(genre.id);
      let isExpanded = expanded.includes(genre.id);

      if (this.genres.has(genre.id)) {
        let existing = this.genres.get(genre.id);
        let pos = layout[genre.id];
        existing.set_target(pos.x, pos.y);
        existing.selected = isSelected;
        existing.expanded = isExpanded;
      } else {
        let pos = layout[genre.id];
        let rel = relationships.find(r => r.target === genre.id);
        let x = rel ? layout[rel.source].x : 0.5;
        let y = rel ? layout[rel.source].y : 0.5;

        let g = new Genre(this.p, genre.id, genre.name, genre.description, x, y, 10);
        g.set_target(pos.x, pos.y);
        g.isExpandable = genre.has_subgenre;
        g.isSelectable = genre.is_selectable;
        g.selected = isSelected;
        g.expanded = isExpanded;
        g.depth = genre.depth;
        this.genres.set(genre.id, g);
        this.drawQueue.push(genre.id);
      }
    });

    const validIds = new Set(genres.map(g => g.id));
    for (let id of this.genres.keys()) {
      if (!validIds.has(id)) {
          this.genres.delete(id);
          let index = this.drawQueue.indexOf(id);
          if (index !== -1) this.drawQueue.splice(index, 1);
      }
    }



    this.update_highlight(highlight);



    this.relationships = relationships;
  }

  drawDashedLineFlow(x1, y1, x2, y2, dashLength = 10, gap = 5, speed = 2) {
    let dx = x2 - x1;
    let dy = y2 - y1;
    let len = this.p.dist(x1, y1, x2, y2);
    let angle = this.p.atan2(dy, dx);

    let offset = this.p.frameCount * speed % (dashLength + gap);
    let current = offset;

    this.p.push();
    this.p.translate(x1, y1);
    this.p.rotate(angle);

    while (current < len) {
      let start = current;
      let end = this.p.min(current + dashLength, len);
      this.p.line(start, 0, end, 0);
      current += dashLength + gap;
    }
    this.p.pop();
  }

  draw() {
    let pad = 64;
    let w = this.p.width - 2 * pad;
    let h = this.p.height - 2 * pad;

    for (const relationship of this.relationships) {
      this.p.strokeWeight(1);
      this.p.stroke(0);
      let source = this.genres.get(relationship.source);
      let target = this.genres.get(relationship.target);
      if (source && target) {
        this.p.strokeWeight(2);
        if (source.selected && target.selected) {
          this.p.strokeWeight(4);
        }
        switch (relationship.type) {
          case "SUBGENRE_OF":
            this.p.strokeWeight(4);
            this.p.stroke(0, 255, 0);
            break;
          case "INFLUENCED_BY":
            this.p.strokeWeight(10);
            this.p.stroke(255, 60);
            break;
          case "FUSION_OF":
            this.p.strokeWeight(3);
            this.p.stroke(0, 0, 255);
            break;
          default:
            this.p.stroke(0);
          // code if no case matches
        }
        this.drawDashedLineFlow(source.x * w + pad, source.y * h + pad, target.x * w + pad, target.y * h + pad, 1, 12, 0.5)
      }
    }


    for (let item of [...this.drawQueue].reverse()) {
      let highlight = false;
      if (this.highlight === item) {
          highlight = true;
      }
      this.genres.get(item).draw(pad, w, h, highlight);
    }
  }

  mousePressed() {
    let pad = 64;
    let w = this.p.width - 2 * pad;
    let h = this.p.height - 2 * pad;
    for (let genre of this.genres.values()) {
      if (genre.isHovered(this.p.mouseX, this.p.mouseY, w, h, pad)) {
        let action = null;
        if (this.p.mouseButton === this.p.LEFT ) {
          action = genre.isExpandable ? "expand" : "highlight";
        } else if (this.p.mouseButton === this.p.RIGHT) {
          action = genre.isSelectable ? "select" : "highlight";
        }
        if (action) {
          this.session.updateOnServer({action: action, id: genre.id }, '/api/graph/update');
        }
      }
    }
  }
  keyPressed() {
    let pad = 64;
    let w = this.p.width - 2 * pad;
    let h = this.p.height - 2 * pad;
    let action = null;
    let genre_id = -1;
    let key = this.p.key;
    if (key === 'r' || key === 'R') { // Check if the "X" key is pressed
      action = "reset";
    }
    if (key === 'c' || key === 'C') { // Check if the "X" key is pressed
      action = "collapse";
    }
    if ((key === 'h' || key === 'f')) { // Check if the "X" key is pressed
      for (let genre of this.genres.values()) {
        if (genre.isHovered(this.p.mouseX, this.p.mouseY, w, h, pad)){
          genre_id = genre.id;
          action = "highlight";
        }
      }

    }
    if (action) {
      this.session.updateOnServer({action: action, id: genre_id }, '/api/graph/update')
    }
  }

  mouseMoved() {
    let pad = 64;
    let w = this.p.width - 2 * pad;
    let h = this.p.height - 2 * pad;
    for (let genre of this.genres.values()) {
      if (genre.isHovered(this.p.mouseX, this.p.mouseY, w, h, pad)) {
        let index = this.drawQueue.indexOf(genre.id);
        if (index !== -1) {
          const [elem] = this.drawQueue.splice(index, 1);
          this.drawQueue.unshift(elem);
        }
      }
    }
  }
}

