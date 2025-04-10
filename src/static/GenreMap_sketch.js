let genreMapSketch = (p) => {
  let genre_map;
  p.setup = () => {
    p.createCanvas(p.windowWidth * 2 / 3, p.windowHeight);
    p.background(60);
    genre_map = new GenreMap(p);
  };

  p.draw = () => {
    p.background(100);
    genre_map.update(0.05);
    genre_map.draw();
    p.strokeWeight(2);
    p.stroke(0);
    p.line(p.mouseX, p.mouseY, p.pmouseX, p.pmouseY);
  };

  p.windowResized = () => {
    p.resizeCanvas(p.windowWidth * 2/3, p.windowHeight);
  };

  p.mousePressed = () => {
    if (inCanvas()) {
      genre_map.mousePressed();
    }
  };

  p.keyPressed = () => {
    if (inCanvas()) {
      genre_map.keyPressed();
    }
  };

  p.mouseMoved = () => {
    if (inCanvas()) {
      genre_map.mouseMoved();
    }
  };

  function inCanvas(){
    return p.mouseX > 0 && p.mouseX < p.width && p.mouseY > 0 && p.mouseY < p.height
  }
};

new p5(genreMapSketch, 'left-sketch-1');
