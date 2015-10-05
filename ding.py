#!/usr/bin/env python
def tileHash(points):
  return points[0] * 100 + points[0]

TILE_UNICODE_MAP = {
  tileHash([1, 1]) : 127033,
  tileHash([1, 3]) : 127035, tileHash([3, 1]) : 127046,
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

class Board():
  """docstring for Board"""
  def __init__(self):
    self.tiles = []
    self.left = 0
    self.right = 0
      
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
    self.discards = []

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

  def getTotalCount(self):
    return sum(self.discards)
    
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
    Tile(6, 6), Tile(6, 6),
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
      player.setHands([Tile.createsFrom(self.tileSet[i]) for i in a[start:end]])

  def start(self):
    self.board = Board()
    self._dealTiles()
    # totoal 6 rounds 
    rounds = len(self.tileSet) / len(self.players)
    for x in range(rounds):
      for player in self.players:
        player.deal(self.board)

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
  tiles = [Tile(1,2), Tile(1,4), Tile(1,6), Tile(4, 2)]
  board.add(True, tiles[0])
  print str(board)
  board.add(True, tiles[2])
  print str(board)
  board.add(False, tiles[3])
  print str(board)
  board.add(False, tiles[1])
  print str(board)

def gameTest():
  game = Game()
  game.addPlayer(Player('Addey'))
  game.addPlayer(Player('Beddy'))
  game.addPlayer(Player('Colly'))
  game.addPlayer(Player('Denny'))
  game.start()

gameTest()

