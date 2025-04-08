let genre_map;


function setup() {
  createCanvas(windowWidth, windowHeight);
  background(60);
  genre_map = new GenreMap();
  document.oncontextmenu = () => false;
}

function draw() {
  background(65);

  genre_map.update(0.05);
  genre_map.draw();
  strokeWeight(2);
  stroke(0);
  line(mouseX, mouseY, pmouseX, pmouseY);
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}

function mousePressed() {
  genre_map.mousePressed();
}

function keyPressed() {
  genre_map.keyPressed();
}

function mouseMoved() {
  genre_map.mouseMoved();
}
