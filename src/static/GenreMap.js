let rel_color = "#016FB9"

class Genre {
  constructor(id, name, x, y, r) {
    this.id = id;
    this.name = name;
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
  }

  set_target(x, y) {
    this.target_x = x;
    this.target_y = y;
  }

  update(rate) {
    this.x = lerp(this.x, this.target_x, rate)
    this.y = lerp(this.y, this.target_y, rate)
  }

  isHovered(px, py, w, h, pad) {
    const gx = this.x * w + pad;
    const gy = this.y * h + pad;
    return dist(px, py, gx, gy) <= this.r * 2;
  }

  draw(pad, w, h) {
    let x = this.x * w + pad;
    let y = this.y * h + pad;
    let r = this.isExpandable ? 20 : 13;

    let factor = 8- Number(this.depth)

    fill(0)
    stroke(0)
    strokeWeight(2);

    if (this.selected) {
      fill("#FF6500");
    }
    if (this.expanded) {
      stroke(rel_color);
    }



    circle(x, y, r);

    strokeWeight(5);
    stroke(0)
    fill(255);
    textAlign(CENTER, CENTER);
    textSize(15);
    text(this.name, x, y - r);
  }
}


class GenreMap {
  constructor() {
    this.session = session;
    this.genres = new Map();
    this.relationships = [];
    this.radius = 10;

    this.selected = [];
    this.expanded = [];

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

  update_graph_from_session(data) {
    console.log(data)
    const { genres: genres, relationships: relationships, layout: layout, state: state } = data;
    const { selected: selected, expanded: expanded } = state;

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

        let g = new Genre(genre.id, genre.name, x, y, 10);
        g.set_target(pos.x, pos.y);
        g.isExpandable = genre.has_subgenres;
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

    this.relationships = relationships;
  }

  drawDashedLineFlow(x1, y1, x2, y2, dashLength = 10, gap = 5, speed = 2) {
    let dx = x2 - x1;
    let dy = y2 - y1;
    let len = dist(x1, y1, x2, y2);
    let angle = atan2(dy, dx);

    let offset = frameCount * speed % (dashLength + gap);
    let current = offset;

    push();
    translate(x1, y1);
    rotate(angle);

    while (current < len) {
      let start = current;
      let end = min(current + dashLength, len);
      line(start, 0, end, 0);
      current += dashLength + gap;
    }
    pop();
  }

  draw() {
    let pad = 64;
    let w = width - 2 * pad;
    let h = height - 2 * pad;

    for (const relationship of this.relationships) {
      strokeWeight(1);
      stroke(0);
      let source = this.genres.get(relationship.source);
      let target = this.genres.get(relationship.target);
      if (source && target) {
        strokeWeight(2);
        if (source.selected && target.selected) {
          strokeWeight(4);
        }
        switch (relationship.type) {
          case "SUBGENRE_OF":
            strokeWeight(4);
            stroke(0, 255, 0);
            break;
          case "INFLUENCED_BY":
            strokeWeight(10);
            stroke(180);
            // code for case "b"
            break;
          case "FUSION_OF":
            strokeWeight(3);
            stroke(0, 0, 255);

            break;
          default:
            stroke(0);
          // code if no case matches
        }
        this.drawDashedLineFlow(source.x * w + pad, source.y * h + pad, target.x * w + pad, target.y * h + pad, 1, 12, 0.5)
      }
    }

    //console.log(this.drawQueue)
    for (let item of [...this.drawQueue].reverse()) {

      this.genres.get(item).draw(pad, w, h);
    }
  }

  mousePressed() {
    let pad = 64;
    let w = width - 2 * pad;
    let h = height - 2 * pad;
    for (let genre of this.genres.values()) {
      if (genre.isHovered(mouseX, mouseY, w, h, pad)) {
        const action = mouseButton === LEFT ? "expand" : "select";
        this.session.updateOnServer({action: action, id: genre.id }, '/api/graph/update');
      }
    }
  }
  keyPressed() {
    let action = null;
    if (key === 'r' || key === 'R') { // Check if the "X" key is pressed
      action = "reset";
    }
    if (key === 'c' || key === 'C') { // Check if the "X" key is pressed
      action = "collapse";
    }
    if (action) {
      this.session.updateOnServer({action: action, id: -1 }, '/api/graph/update')
    }
  }

  mouseMoved() {
    let pad = 64;
    let w = width - 2 * pad;
    let h = height - 2 * pad;
    for (let genre of this.genres.values()) {
      if (genre.isHovered(mouseX, mouseY, w, h, pad)) {
        let index = this.drawQueue.indexOf(genre.id);
        if (index !== -1) {
          const [elem] = this.drawQueue.splice(index, 1);
          this.drawQueue.unshift(elem);
        }
      }
    }
  }
}

