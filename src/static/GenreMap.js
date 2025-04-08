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
        strokeWeight(2);
        stroke(100);
        noFill();
        if (this.selected) {
            strokeWeight(2);
            stroke(255, 0, 0);
        }
        if (this.expanded) {
            fill(0, 255, 255)
        }
        let n = 2;
        if (this.isExpandable) {
            rect(this.x * w + pad, this.y * h + pad, this.r * n, this.r * n)
        }
        circle(this.x * w + pad, this.y * h + pad, this.r * n);
        strokeWeight(5);
        stroke(0);
        fill(255);
        textAlign(CENTER, CENTER);
        textSize(15);
        text(this.name, this.x * w + pad, this.y * h + pad - 10);
    }
}


class GenreMap {
    constructor() {
        this.reset()
        this.genres = new Map();
        this.relationships = [];
        this.radius = 10;

        this.selected = [];
        this.expanded = [];

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

    update_with(url) {
        fetch(url)
        .then(response => response.json())
        .then(data => {this.update_graph(data)});
    }

    init_graph() {
        this.update_with(`/api/graph/initial_graph/`);
    }

    update_graph(json_data) {
        let genres = json_data.graph.nodes;
        let relationships = json_data.graph.links;
        let layout = json_data.layout;
        let data = json_data.data;
        let expanded = data.expanded;
        let selected = data.selected;


        genres.forEach(genre => {
            let isSelected = selected.includes(genre.id);
            let isExpanded = expanded.includes(genre.id);
            let isSpotifyGenre = genre.spotify_genre
            if (this.genres.has(genre.id)) {
                let existing_genre = this.genres.get(genre.id);
                let pos = layout[genre.id];
                existing_genre.set_target(pos.x, pos.y);
                existing_genre.selected = isSelected;
                existing_genre.expanded = isExpanded;
            } else {
                let x = 0.5;
                let y = 0.5;
                let pos = layout[genre.id];

                let rel = relationships.find(r => r.target === genre.id);
                if (rel) {
                    x = layout[rel.source].x;
                    y = layout[rel.source].y;
                }

                let g = new Genre(genre.id, genre.name, x, y, 10);
                g.set_target(pos.x, pos.y);
                g.isExpandable = genre.has_children;
                g.selected = isSelected;
                g.expanded = isExpanded;
                this.genres.set(genre.id, g);
            }
        });

        const validIds = new Set(genres.map(g => g.id));
        for (let id of this.genres.keys()) {
            if (!validIds.has(id)) {
                this.genres.delete(id);
            }
        }
        this.relationships = relationships.map(edge => [Number(edge.source), Number(edge.target)]);
    }

    draw() {
        let pad = 64;
        let w = width - 2 * pad;
        let h = height - 2 * pad;

        for (const relationship of this.relationships) {
            strokeWeight(1);
            stroke(0);
            let source = this.genres.get(relationship[0]);
            let target = this.genres.get(relationship[1]);
            if (source && target) {
                if (source.selected && target.selected) {
                    strokeWeight(3);
                    stroke(0, 0, 255);
                }
                line(source.x * w + pad, source.y * h + pad, target.x * w + pad, target.y * h + pad);
            }
        }


        for (let genre of this.genres.values()) {
            genre.draw(pad, w, h);
        }
    }

    mousePressed() {
        let pad = 64;
        let w = width - 2 * pad;
        let h = height - 2 * pad;
        for (let genre of this.genres.values()) {
            if (genre.isHovered(mouseX, mouseY, w, h, pad)) {
                if (mouseButton === RIGHT) {
                    this.update_with(`/api/graph/genre/${genre.id}`);
                } else if (mouseButton === LEFT) {
                    this.update_with(`/api/graph/subgenres/${genre.id}`);
                }
                break;
            }
        }
    }
    keyPressed() {
        if (key === 'r' || key === 'R') { // Check if the "X" key is pressed
            this.update_with("api/graph/reset")
        }
        if (key === 'c' || key === 'C') { // Check if the "X" key is pressed
            this.update_with("api/graph/collapse_all")
        }
    }
}

