var drawCircle = function(context, x, y, radius, color) {
  context.beginPath();
  context.arc(x, y, radius, 0, 2 * Math.PI, false);
  context.fillStyle = color;
  context.fill();
}

var tileHash = function(tile) {
  return (tile[0] * 100 + tile[1]).toString();
}

var tileToDots = {};
tileToDots[tileHash([0,0])] = '-------' + '-------';
tileToDots[tileHash([1,1])] = '---r---' + '---r---';
tileToDots[tileHash([1,3])] = '---r---' + '-w-w-w-';
tileToDots[tileHash([1,5])] = '---r---' + 'ww-w-ww';
tileToDots[tileHash([1,6])] = '---r---' + 'www-www';
tileToDots[tileHash([2,2])] = 'ww-----' + '-----ww';
tileToDots[tileHash([2,6])] = 'ww-----' + 'www-www';
tileToDots[tileHash([3,1])] = '-w-w-w-' + '---r---';
tileToDots[tileHash([3,3])] = '-w-w-w-' + '-w-w-w-';
tileToDots[tileHash([3,6])] = '-w-w-w-' + 'www-www';
tileToDots[tileHash([4,4])] = 'rrr-r--' + '--r-rrr';
tileToDots[tileHash([4,6])] = 'rrr-r--' + 'www-www';
tileToDots[tileHash([5,1])] = 'ww-w-ww' + '---r---';
tileToDots[tileHash([5,5])] = 'ww-w-ww' + 'ww-w-ww';
tileToDots[tileHash([5,6])] = 'ww-w-ww' + 'www-www';
tileToDots[tileHash([6,1])] = 'www-www' + '---r---';
tileToDots[tileHash([6,2])] = 'www-www' + '-----ww';
tileToDots[tileHash([6,3])] = 'www-www' + '-w-w-w-';
tileToDots[tileHash([6,4])] = 'www-www' + '--r-rrr';
tileToDots[tileHash([6,5])] = 'www-www' + 'ww-w-ww';
tileToDots[tileHash([6,6])] = 'rwr-wrw' + 'wrw-rwr';

/**
 * Creates a div element for the given tile.
 * 
 * @param {number[]} tile - The tile in points form. e.g. [3, 6].
 * @param {number} size - The size in px of the tile's width.
 * @returns A div element that contains the rendered tile.
 */
createTile = function(tile, size, isRotate){
  var div = document.createElement('div');
  var canvas = document.createElement('canvas');
  var width = 9 * size;
  var height = 20 * size;
  var round = 1 * size;
  div.appendChild(canvas);
  if (isRotate){
    canvas.width = height;
    canvas.height = width;
    div.style.width = height + 'px';
    div.style.height = width + 'px';
  } else {
    canvas.width = width;
    canvas.height = height;
    div.style.width = width + 'px';
    div.style.height = height + 'px';
  };


  div.style.backgroundColor = 'black';
  div.style.borderRadius = round + 'px';

  var context = canvas.getContext('2d');
  var baseX = width / 10;
  var baseY = height / 10;
  var radius = size * 1.4;

  var dots = [];
  dots.push([ 3 * baseX, 1.2 * baseY]);
  dots.push([ 7 * baseX, 1.2 * baseY]);

  dots.push([ 3 * baseX, 2.7 * baseY]);
  dots.push([ 5 * baseX, 2.7 * baseY]);
  dots.push([ 7 * baseX, 2.7 * baseY]);

  dots.push([ 3 * baseX, 4.2 * baseY]);
  dots.push([ 7 * baseX, 4.2 * baseY]);

  dots.push([ 3 * baseX, 5.8 * baseY]);
  dots.push([ 7 * baseX, 5.8 * baseY]);

  dots.push([ 3 * baseX, 7.3 * baseY]);
  dots.push([ 5 * baseX, 7.3 * baseY]);
  dots.push([ 7 * baseX, 7.3 * baseY]);

  dots.push([ 3 * baseX, 8.8 * baseY]);
  dots.push([ 7 * baseX, 8.8 * baseY]);

  var drawDot = function(id, color, isRotate) {
    if (isRotate) {
      drawCircle(context, dots[id][1], dots[id][0], radius, color);
    } else {
      drawCircle(context, dots[id][0], dots[id][1], radius, color);
    };
  }

  var tileDots = tileToDots[tileHash(tile)];
  for (var i = 0; i < dots.length; i++) {
    switch(tileDots[i]) {
      case 'w':
        drawDot(i, 'white', isRotate);
        break;
      case 'r':
        drawDot(i, 'OrangeRed', isRotate);
        break;
      default:
      break;
    }
  };
  return div;
}

