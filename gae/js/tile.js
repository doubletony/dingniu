/**
 * Creates a div element for the given tile.
 * 
 * @param {number[]} tile - The tile in points form. e.g. [3, 6].
 * @param {number} size - The size in px of the tile's width.
 * @returns A div element that contains the rendered tile.
 */
CreateTile = function(tile, size){
  var div = document.createElement('div');
  var canvas = document.createElement('canvas');
  var width = 10 * size;
  var height = 20 * size;
  var round = 1.5 * size;
  div.appendChild(canvas);
  canvas.width = width;
  canvas.height = height;

  div.style.width = width + 'px';
  div.style.height = height + 'px';
  div.style.backgroundColor = 'black';
  div.style.borderRadius = round + 'px';

  var context = canvas.getContext('2d');
  var centerX = canvas.width / 2;
  var centerY = canvas.height / 4;
  var radius = size * 1;

  context.beginPath();
  context.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
  context.fillStyle = 'white';
  context.fill();

  context.beginPath();
  context.arc(centerX, centerY * 3, radius, 0, 2 * Math.PI, false);
  context.fillStyle = 'white';
  context.fill();
  return div;
}

BoardRender = function(div){
  this.div = div;
};

BoardRender.prototype.add = function(isLeft, tile){
  var tile = CreateTile(tile, 6);
  this.div.appendChild(tile);
};
