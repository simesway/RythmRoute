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

        this.add_genre(6598)
        this.add_genre(1)
        this.add_genre(5)
        this.add_genre(3)
        this.add_genre(20)
        this.add_genre(379)
        this.add_genre(523)
        this.add_genre(99)
        this.add_genre(151)
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
        fetch(`/api/genre/${genre_id}`)
        .then(response => response.json())
        .then(data => {this.update_graph(data)});
    }

    add_subgenres(genre_id) {
        fetch(`/api/subgenres/${genre_id}`)
        .then(response => response.json())
        .then(data => {this.update_graph(data, genre_id)});
    }

    update_graph(json_data, genre_id) {
        let nodes = json_data.genres
        let edges = json_data.relationships;

        let pad = 100;
        let w = width - 2 * pad;
        let h = height - 2 * pad;

        // update genres
        for (let id in nodes) {
            let node = nodes[id]
            if (this.genres.has(id)) {
                let genre = this.genres.get(id);
                genre.set_target(node.x, node.y);
                //genre.r = node.centrality;
                this.genres.set(id, genre);
            } else {
                let x = 0.5;
                let y = 0.5;
                let tx = node.x;
                let ty = node.y;
                let r = node.r;

                if (genre_id && this.genres.has(genre_id) && false) {
                    let parent_genre = nodes[genre_id];
                    x = parent_genre.x;
                    y = parent_genre.y;
                }
                console.log(node)

                let genre = new Genre(id, node.name, x, y, 10);
                genre.set_target(tx, ty);
                this.genres.set(id, genre);
            }
        }

        this.relationships = edges.map(edge => [Number(edge.source), Number(edge.target)]);
    }

    scaleNumber(value, oldMin, oldMax, newMin, newMax) {
    // Ensure the old range is valid
        if (oldMax === oldMin) {
            throw new Error("Old range is invalid: oldMin and oldMax cannot be the same.");
        }

        // Scale the number
        const scaledValue = ((value - oldMin) / (oldMax - oldMin)) * (newMax - newMin) + newMin;
        return scaledValue;
    }

    render_metaballs() {
      loadPixels();
      for (let x = 0; x < width; x++) {
        for (let y = 0; y < height; y++) {
          let sum = 0;
          for (let genre of this.genres.values()) {
            let xdif = x - genre.x;
            let ydif = y - genre.y;
            let d = sqrt((xdif * xdif) + (ydif * ydif));
            sum += 12 * genre.r / d;
          }

          sum = sum % 20 * 20

            let r = this.scaleNumber(sum, 0, 200, 0, 2);
          let g = this.scaleNumber(sum, 0, 200, 0, 48);

          let b = this.scaleNumber(sum, 0, 200, 0, 32);



          set(x, y, color(r, g, b));
        }
      }
      updatePixels();
    }

    show(dot) {
        let pad = 64;
        let w = width - 2 * pad;
        let h = height - 2 * pad;

        for (const [source_id, target_id] of this.relationships) {
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
              this.add_subgenres(genre.id);
              genre.selected = !genre.selected;
              break;
            }
        }
    }
}

