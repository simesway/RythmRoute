class MovingPoint {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.target_x = 0;
    this.target_y = 0;
  }

  set_target(x, y) {
    this.target_x = x;
    this.target_y = y;
  }

  update(p, rate) {
    this.x = p.lerp(this.x, this.target_x, rate);
    this.y = p.lerp(this.y, this.target_y, rate);
  }
}

class GenreMap {
  constructor(p) {
    this.p = p;
    this.session = session;
    this.genre_manager = genre_manager;

    this.layout = new Map();
    this.relationships = [];


    this.pad = 64;
    this.w = this.p.width - 2 * this.pad;
    this.h = this.p.height - 2 * this.pad;

    this.session.subscribe((state) => {
      this.update_graph(state.graph);
    });

    this.session.fetchState();
  }

  update(rate) {
    for (let point of this.layout.values()) {
      point.update(this.p, rate);
    }
  }

  update_graph(data) {
  const { relationships, layout } = data;

  // Only keep entries that exist in genre_manager
  const valid_ids = new Set(Object.keys(layout).filter(id => this.genre_manager.has(id)));

  // Update layout
  for (const id of valid_ids) {
    const pos = layout[id];
    if (this.layout.has(id)) {
      this.layout.get(id).set_target(pos.x, pos.y);
    } else {
      const rel = relationships.find(r => r.target === id);
      const fallback = rel ? layout[rel.source] : { x: 0.5, y: 0.5 };
      const mp = new MovingPoint(fallback.x, fallback.y);
      mp.set_target(pos.x, pos.y);
      this.layout.set(id, mp);
    }
  }

  // Remove stale layout points
  for (const id of this.layout.keys()) {
    if (!valid_ids.has(id)) {
      this.layout.delete(id);
    }
  }

  // Filter relationships to only include valid genres
  this.relationships = relationships.filter(r =>
    valid_ids.has(String(r.source)) && valid_ids.has(String(r.target))
  );
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

  get_coords(x, y) {
    return { x: x * this.w + this.pad, y: y * this.h + this.pad}
  }

  draw_genre(genre_id) {
    let genre = this.genre_manager.get(genre_id);
    let pos = this.layout.get(genre_id);
    const {x: x, y: y} = this.get_coords(pos.x, pos.y);

    let r = genre.hasSubgenre ? 24 : 13;

    if (false) {
      this.p.fill(255, 0, 0);
      this.p.noStroke()
      this.p.circle(x, y, r+10)
    }

    this.p.fill(180);
    this.p.noStroke();

    if (genre.isSelectable) {
      this.p.fill(30);
    }
    if (this.genre_manager.isSelected(genre_id)) {
      this.p.fill("#FF6500");
    }

    if (genre.hasSubgenre) {
      this.p.strokeWeight(5);
      this.p.stroke("#FC6FB9");
    }
    if (this.genre_manager.isExpanded(genre_id)) {
      this.p.stroke("#016FB9");
    }

    this.p.circle(x, y, r);

    this.p.strokeWeight(5);
    this.p.stroke(0)
    this.p.fill(255);
    this.p.textAlign(this.p.CENTER, this.p.CENTER);
    this.p.textSize(15);
    this.p.text(genre.name, x, y - r);
  }


  draw() {

    for (const relationship of this.relationships) {
      let s_id = String(relationship.source);
      let t_id = String(relationship.target);
      let source = this.layout.get(s_id);
      let target = this.layout.get(t_id);
      this.p.strokeWeight(1);
      this.p.stroke(0);
      if (source && target) {
        this.p.strokeWeight(2);
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
        const { x: x1, y: y1 } = this.get_coords(source.x, source.y);
        const { x: x2, y: y2 } = this.get_coords(target.x, target.y);
        this.drawDashedLineFlow(x1, y1, x2, y2, 1, 12, 0.5);
      }
    }


    for (const genre_id of this.layout.keys()) {
      this.draw_genre(genre_id);
    }
  }

  mousePressed() {
    let pad = 64;
    let w = this.p.width - 2 * pad;
    let h = this.p.height - 2 * pad;
    for (let [genre_id, pos] of this.layout) {
      let genre = this.genre_manager.get(genre_id);
      const { x: x, y: y } = this.get_coords(pos.x, pos.y);
      let d = this.p.dist(this.p.mouseX, this.p.mouseY, x, y);
      let r = 20;
      if (d <= r) {
        let action = null;
        if (this.p.mouseButton === this.p.LEFT ) {
          action = genre.hasSubgenre ? "expand" : "highlight";
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
    if (action) {
      this.session.updateOnServer({action: action, id: genre_id }, '/api/graph/update')
    }
  }

  mouseMoved() {
  }
}