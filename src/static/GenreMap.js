class Genre {
    constructor(id, name, x, y, r) {
        this.id = id;
        this.name = name;
        this.x = x;
        this.y = y;
        this.r = r;

        this.target_x = x;
        this.target_y = y;

        this.selected = false;
    }

    set_target(x, y) {
        this.target_x = x;
        this.target_y = y;
    }

    update(rate) {
        this.x = lerp(this.x, this.target_x, rate)
        this.y = lerp(this.y, this.target_y, rate)
    }

    show(radius, label) {
        if (radius) {
            noFill();
            stroke(255, 0, 0);
            strokeWeight(3);
            ellipse(this.x, this.y, this.r * 2, this.r * 2);
        }
        if (label) {
            fill(0, 0, 255);
            textAlign(CENTER);
            textSize(10);
            text(this.name, this.x, this.y);
        }
    }
}


class GenreMap {
    constructor() {
        this.reset()
        this.genres = new Map();
        this.relationships = [];
        this.radius = 10;

        this.init_graph()
    }

    update(rate) {
        for (let genre of this.genres.values()) {
            genre.update(rate)
        }
    }

    reset() {
        fetch("/api/reset")
    }

    add_genre(genre_id) {
        fetch(`/api/select/genre/${genre_id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json', // Set the request type to JSON
          },
          body: JSON.stringify(genre_id), // Convert the data to a JSON string
        });
    }

    add_subgenres(genre_id) {
        fetch(`/api/subgenres/${genre_id}`)
        .then(response => response.json())
        .then(data => {this.update_graph(data, genre_id)});
    }

    init_graph() {
        fetch(`/api/graph/initial_graph/`)
        .then(response => response.json())
        .then(data => {this.update_graph(data)});
    }

    update_graph(json_data) {
        let genres = json_data.graph.nodes;
        let relationships = json_data.graph.links;
        let layout = json_data.layout;


        genres.forEach(genre => {
          if (this.genres.has(genre.id)) {
              let existing_genre = this.genres.get[genre.id];
              let pos = layout[genre.id]
              existing_genre.set_target(pos.x, pos.y)
          } else {
              let x = 0.5;
              let y = 0.5;
              let pos = layout[genre.id];

              let rel = relationships.find(item => item.target === genre.id);
              if (rel) {
                  x = layout[rel.source].x
                  y = layout[rel.source].y
              }

              let new_genre = new Genre(genre.id, genre.name, x, y, 10);
              new_genre.set_target(pos.x, pos.y);
              this.genres.set(genre.id, new_genre);
          }
        });
        this.relationships = relationships.map(edge => [Number(edge.source), Number(edge.target)]);

        console.log(this.genres)
        console.log(this.relationships)
    }

    show(dot) {
        let pad = 64;
        let w = width - 2 * pad;
        let h = height - 2 * pad;

        for (const [source_id, target_id, type] of this.relationships) {
            strokeWeight(1);
            stroke(0);
            let source = this.genres.get(String(source_id));
            let target = this.genres.get(String(target_id));
            if (source && target) {
                if (source.selected && target.selected) {
                    strokeWeight(3);
                    stroke(0, 0, 255);
                }
                line(source.x * w + pad, source.y * h + pad, target.x * w + pad, target.y * h + pad);
            }
        }


        for (let genre of this.genres.values()) {
            strokeWeight(2);
            if (dot) {
                stroke(100);
                noFill();
                if (genre.selected) {
                    strokeWeight(2);
                    stroke(0, 0, 255);
                }
                let n = 2;
                circle(genre.x * w + pad, genre.y * h + pad, genre.r * n);
            }
            strokeWeight(3);
            stroke(0);
            fill(255);
            textAlign(CENTER, CENTER);
            textSize(20);
            text(genre.name, genre.x * w + pad, genre.y * h + pad - 10);
        }
    }

    mousePressed() {
        let pad = 64;
        let w = width - 2 * pad;
        let h = height - 2 * pad;
        for (let genre of this.genres.values()) {
            let d = dist(mouseX, mouseY, genre.x * w + pad, genre.y * h + pad);
            if (d <= genre.r * 2) {
                this.add_genre(genre.id);
              genre.selected = !genre.selected;
              break;
            }
        }
    }
}

