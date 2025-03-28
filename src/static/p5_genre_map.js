let genre_map;


function setup() {
  createCanvas(windowWidth, windowHeight);
  background(35);
  // Fetch graph data from Python API
  genre_map = new GenreMap();
}

function draw() {
  background(180);

  genre_map.update(0.01);
  genre_map.show(true);
  strokeWeight(2);
  stroke(20);
  line(mouseX, mouseY, pmouseX, pmouseY);
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}

function mousePressed() {
  genre_map.mousePressed()
}