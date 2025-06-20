let container_id = 'genre-graph';

let genreMapSketch = (p) => {
  let genre_map;
  let canvas;

  p.setup = () => {
    const container = document.getElementById(container_id);
    const w = container.offsetWidth;
    const h = container.offsetHeight;
    canvas = p.createCanvas(w, h);
    canvas.parent(container);
    genre_map = new GenreMap(p);
    canvas.elt.oncontextmenu = () => false;
  };

  p.draw = () => {
    p.background("#EEE");
    genre_map.update(0.05);
    genre_map.draw();
    p.strokeWeight(2);
    p.stroke(0);
    p.line(p.mouseX, p.mouseY, p.pmouseX, p.pmouseY);
  };

  p.windowResized = () => {
    const container = document.getElementById(container_id);
    const w = container.offsetWidth;
    const h = container.offsetHeight;
    p.resizeCanvas(w, h);
    genre_map.windowResized(w, h);
  };

  p.mousePressed = () => {
    if (inCanvas()) genre_map.mousePressed();
  };

  p.keyPressed = () => {
    if (inCanvas()) genre_map.keyPressed();
  };

  p.mouseMoved = () => {
    if (inCanvas()) genre_map.mouseMoved();
  };

  function inCanvas() {
    return p.mouseX > 0 && p.mouseX < p.width && p.mouseY > 0 && p.mouseY < p.height;
  }
};

new p5(genreMapSketch, container_id);
