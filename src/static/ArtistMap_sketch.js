import ArtistMap from './ArtistMap.js';

let artistMapSketch = (p) => {
  let artist_map;
  let canvas;

  p.setup = () => {
    const container = document.getElementById('artist-map');
    const w = container.offsetWidth;
    const h = container.offsetHeight;
    canvas = p.createCanvas(w, h);
    canvas.parent(container);
    artist_map = new ArtistMap(p);
    canvas.elt.oncontextmenu = () => false;
    p.frameRate(10);
  };

  p.draw = () => {
    p.background("#EEE");

    artist_map.draw();
  };

  p.windowResized = () => {
    const container = document.getElementById('artist-map');
    const w = container.offsetWidth;
    const h = container.offsetHeight;
    p.resizeCanvas(w, h);
  };

  p.keyPressed = () => {
    if (inCanvas()) artist_map.keyPressed();
  }

  function inCanvas(){
    return p.mouseX > 0 && p.mouseX < p.width && p.mouseY > 0 && p.mouseY < p.height
  }
};

new p5(artistMapSketch, 'artist-map');
