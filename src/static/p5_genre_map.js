let genre_map;


function setup() {
  createCanvas(windowWidth, windowHeight);
  background(35);
  genre_map = new GenreMap();

  document.oncontextmenu = () => false;
}

function draw() {
  background(180);

  genre_map.update(0.05);
  genre_map.draw();
  strokeWeight(2);
  stroke(20);
  line(mouseX, mouseY, pmouseX, pmouseY);
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}

function mousePressed() {
  genre_map.mousePressed();
}

function keyPressed() {
  genre_map.keyPressed()
}
