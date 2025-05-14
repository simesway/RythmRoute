import ArtistMap from './ArtistMap.js';

let artistMapSketch = (p) => {
  let artist_map;
  p.setup = () => {
    p.createCanvas(p.windowWidth * 2 / 3, p.windowHeight * 2/3);
    p.background(60);
    artist_map = new ArtistMap(p);

  };

  p.draw = () => {
    p.background(120);

    artist_map.draw();
    p.strokeWeight(2);
    p.stroke(0);
    p.line(p.mouseX, p.mouseY, p.pmouseX, p.pmouseY);
  };

  p.windowResized = () => {
    p.resizeCanvas(p.windowWidth * 2/3, p.windowHeight * 2/3);
  };

  p.keyPressed = () => {
    artist_map.keyPressed()
  }

  function inCanvas(){
    return p.mouseX > 0 && p.mouseX < p.width && p.mouseY > 0 && p.mouseY < p.height
  }
};

new p5(artistMapSketch, 'left-sketch-2');
