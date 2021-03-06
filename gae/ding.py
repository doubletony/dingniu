#!/usr/bin/env python
def tileHash(points):
  return points[0] * 100 + points[1]

TILE_UNICODE_MAP = {
  # http://www.alanwood.net/unicode/domino-tiles.html
  tileHash([1, 1]) : 127033,
  tileHash([1, 3]) : 127035, tileHash([3, 1]) : 127047,
  tileHash([1, 5]) : 127037, tileHash([5, 1]) : 127061,
  tileHash([1, 6]) : 127038, tileHash([6, 1]) : 127068,
  tileHash([2, 2]) : 127041,
  tileHash([2, 6]) : 127045, tileHash([6, 2]) : 127069,
  tileHash([3, 3]) : 127049,
  tileHash([3, 6]) : 127052, tileHash([6, 3]) : 127070,
  tileHash([4, 4]) : 127057,
  tileHash([4, 6]) : 127059, tileHash([6, 4]) : 127071,
  tileHash([5, 5]) : 127065,
  tileHash([5, 6]) : 127066, tileHash([6, 5]) : 127072,
  tileHash([6, 6]) : 127073
}

class Tile():
  """docstring for Tile"""
  def __init__(self, left, right):
    self.left = left
    self.right = right

  @staticmethod
  def createsFrom(tile):
    return Tile(tile.left, tile.right)

  def __str__(self):
    return '|' + str(self.left) + ' ' + str(self.right) + '|'

  def __unicode__(self):
    return unichr(TILE_UNICODE_MAP[tileHash([self.left, self.right])])

  def getPoints(self):
    return self.left + self.right

class Board():
  """docstring for Board"""
  def __init__(self):
    self.tiles = []
    self.left = 0
    self.right = 0

  def getLeftTile(self):
    return self.tiles[0]

  def getRightTile(self):
    return self.tiles[-1]

  def isAddable(self, tile):
    return self.left == tile.left or self.left == tile.right or self.right == tile.left or self.right == tile.right

  def add(self, isLeft, tile):
    if self.left == 0:
      self.tiles.append(tile)
      self.left = tile.left
      self.right = tile.right
      return
    if isLeft:
      if self.left == tile.left:
        self.tiles.insert(0, Tile(tile.right, tile.left))
        self.left = tile.right
        return
      elif self.left == tile.right:
        self.tiles.insert(0, Tile(tile.left, tile.right))
        self.left = tile.left
        return
    else:
      if self.right == tile.left:
        self.tiles.append(Tile(tile.left, tile.right))
        self.right = tile.right
        return
      elif self.right == tile.right:
        self.tiles.append(Tile(tile.right, tile.left))
        self.right = tile.left
        return
    raise Exception('Cannot add tile to current board', str(tile), str(self))

  def __str__(self):
    s = ''
    for i in self.tiles:
      s = s + str(i)
    return s

  def __unicode__(self):
    s = u' '
    for i in self.tiles:
      print i
      s = s + u' ' + unicode(i)
    return s


class Player():
  """docstring for Player"""
  def __init__(self, name):
    self.name = name
    self.hands = []
    self.discards = []
  
  def setHands(self, tiles):
    self.hands = tiles

  def setDiscards(self, tiles):
    self.discards = tiles

  """Given a board, with current hands, should be able to make a choice to change the board"""
  def deal(self, board):
    print 'Deal a tile, ' + self.name + '!'
    while True:
      print '-' * 80
      print unicode(board)
      print '-' * 80
      for i in range(len(self.hands)):
        print str(i + 1),
        print unicode(self.hands[i])
      command = raw_input("""
  Make a choice, for example, '1L' means append first tile on the left side.
  '1R' means append first tile one the right side.
  '1D' means discard first tile.
  Default command is 'L'.
  """)
      try:
        idx = int(command[0]) - 1
        command = command + 'L'
        choice = command[1]
        if choice.upper() == 'D':
          self.discards.append(self.hands.pop(idx))
          return
        if choice.upper() == 'R':
          tile = self.hands[idx]
          board.add(False, tile)
          self.hands.pop(idx)
          return
        if choice.upper() == 'L':
          tile = self.hands[idx]
          board.add(True, tile)
          self.hands.pop(idx)
          return
        print "[Error!] You made an invalid command."
      except Exception, e:
        print '[Error!] Cannot add the tile.'

  def getTotalPoints(self):
    return sum([i.getPoints() for i in self.discards])

  def getDiscardedTiles(self):
    return self.discards
    
class Game():
  """docstring for Game"""
  def __init__(self):
    self.players = []
    self.tileSet = [
    Tile(1, 1), Tile(1, 1), Tile(1, 3), Tile(1, 3),
    Tile(1, 5), Tile(1, 5), Tile(1, 6), Tile(1, 6),
    Tile(2, 2), Tile(2, 2), Tile(2, 6),
    Tile(3, 3), Tile(3, 3), Tile(3, 6),
    Tile(4, 4), Tile(4, 4), Tile(4, 6), Tile(4, 6),
    Tile(5, 5), Tile(5, 5), Tile(5, 6), Tile(5, 6),
    Tile(6, 6), Tile(6, 6)
    ]

  def addPlayer(self, player):
    self.players.append(player)

  def _dealTiles(self):
    from random import shuffle
    a = range(len(self.tileSet))
    shuffle(a)
    tilesNum = len(self.tileSet) / len(self.players)
    count = 0
    for player in self.players:
      start = count * tilesNum
      end = start + 6
      count += 1
      player.setHands([Tile.createsFrom(self.tileSet[i]) for i in a[start:end]])

  def start(self):
    self.board = Board()
    self._dealTiles()
    # totoal 6 rounds 
    rounds = len(self.tileSet) / len(self.players)
    for x in range(rounds):
      for player in self.players:
        player.deal(self.board)

    print 'Results:'
    points = []
    for player in self.players:
      point = player.getTotalPoints()
      tiles = player.getDiscardedTiles()
      print player.name, 'discarded:',
      for tile in tiles:
        print unicode(tile),
      print ' in total of', point, 'points.'
      points.append(point)
    min_point = min(points)
    max_point = max(points)
    total_award = 0
    BIG_PENALTY = 2
    SMALL_PENALTY = 1
    winner_count = 0

    # Calculate the award amount
    for player in self.players:
      point = player.getTotalPoints()
      if point == max_point:
        total_award += BIG_PENALTY
      elif point > min_point:
        total_award += SMALL_PENALTY
      else:
        # winner
        winner_count += 1

    # Assign the awards and penalty
    for player in self.players:
      point = player.getTotalPoints()
      if point == max_point:
        print player.name, 'loses', '$' + str(BIG_PENALTY)
      elif point > min_point:
        print player.name, 'loses', '$' + str(SMALL_PENALTY)
      else:
        # winner
        print player.name, 'wins', '$' + str(total_award / winner_count)


def tileUnicodeTest():
  tiles = [
  Tile(1, 1), Tile(1, 1), Tile(1, 3), Tile(1, 3),
  Tile(1, 5), Tile(1, 5), Tile(1, 6), Tile(1, 6),
  Tile(2, 2), Tile(2, 2), Tile(2, 6),
  Tile(3, 3), Tile(3, 3), Tile(3, 6),
  Tile(4, 4), Tile(4, 4), Tile(4, 6), Tile(4, 6),
  Tile(5, 5), Tile(5, 5), Tile(5, 6), Tile(5, 6),
  Tile(6, 6), Tile(6, 6)
  ]
  for tile in tiles:
    print str(tile),
    print unicode(tile), unicode(Tile(tile.right, tile.left))

def playerTest():
  board = Board()
  tiles = [Tile(1,2), Tile(1,4), Tile(1,6), Tile(4, 2)]
  turn = len(tiles)
  player = Player('doubletony')
  player.setHands(tiles)
  for i in range(turn):
    player.deal(board)

def boardTest():
  board = Board()
  tiles = [Tile(1,3), Tile(1,3), Tile(1,6), Tile(3, 3)]
  board.add(True, tiles[0])
  print unicode(board)
  board.add(True, tiles[2])
  print unicode(board)
  board.add(False, tiles[3])
  print unicode(board)
  board.add(False, tiles[1])

def gameTest():
  game = Game()
  game.addPlayer(Player('Addey'))
  game.addPlayer(Player('Beddy'))
  game.addPlayer(Player('Colly'))
  game.addPlayer(Player('Denny'))
  game.start()
