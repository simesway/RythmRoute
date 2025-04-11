import ArtistMap from './ArtistMap.js';

let artistMapSketch = (p) => {
  let artist_map;
  p.setup = () => {
    console.log("setup");
    p.createCanvas(p.windowWidth * 2 / 3, p.windowHeight);
    p.background(60);

    artist_map = new ArtistMap(p);

  };

  p.draw = () => {
    p.background(100);
    artist_map.update(0.05);
    artist_map.draw();
    p.strokeWeight(2);
    p.stroke(0);
    p.line(p.mouseX, p.mouseY, p.pmouseX, p.pmouseY);
  };

  p.windowResized = () => {
    p.resizeCanvas(p.windowWidth * 2/3, p.windowHeight);
  };



  function inCanvas(){
    return p.mouseX > 0 && p.mouseX < p.width && p.mouseY > 0 && p.mouseY < p.height
  }
};

new p5(artistMapSketch, 'left-sketch-2');
