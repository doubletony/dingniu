import jinja2
import os
import urllib
import uuid
import webapp2

from google.appengine.ext import ndb
from ding import *

def shuffleTiles(playerNum):
  from random import shuffle
  tileSet = [
    Tile(1, 1), Tile(1, 1), Tile(1, 3), Tile(1, 3),
    Tile(1, 5), Tile(1, 5), Tile(1, 6), Tile(1, 6),
    Tile(2, 2), Tile(2, 2), Tile(2, 6),
    Tile(3, 3), Tile(3, 3), Tile(3, 6),
    Tile(4, 4), Tile(4, 4), Tile(4, 6), Tile(4, 6),
    Tile(5, 5), Tile(5, 5), Tile(5, 6), Tile(5, 6),
    Tile(6, 6), Tile(6, 6)
    ]
  a = range(len(tileSet))
  shuffle(a)
  tilesNum = len(tileSet) / playerNum
  playersHands = []
  count = 0
  for i in range(playerNum):
    start = count * tilesNum
    end = start + 6
    count += 1
    playersHands.append([Tile.createsFrom(tileSet[i]) for i in a[start:end]])
  return playersHands

def parseTile(text):
  text = text.strip('|')
  points = [int(i) for i in text.split()]
  return Tile(points[0], points[1])

def parseBoard(text):
  # assume text is valid from str(Board())
  text = text.strip('|')
  tiles = text.split('||')
  board = Board()
  for tile in tiles:
    if tile == '':
      continue
    board.add(False, parseTile(tile))
  return board


def parseHand(hands):
  tiles = []
  for tile in hands:
    if tile == '':
      continue
    tiles.append(parseTile(tile))
  return tiles

### Starts App Engine Code
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class GameRecord(ndb.Model):
  gameId = ndb.StringProperty(indexed=True)
  board = ndb.StringProperty(indexed=False)
  hands = ndb.JsonProperty(indexed=False)
  cpus = ndb.JsonProperty(repeated=True)

def retriveGame(gameId):
  qry = GameRecord.query(GameRecord.gameId == gameId)
  result = qry.fetch(10)
  if len(result) != 1:
    raise Exception('Faild to fetch game information.', str(len(result)))
  board = parseBoard(result[0].board)
  hands = parseHand(result[0].hands)
  cpus = [parseHand(i) for i in result[0].cpus]
  return board, hands, cpus

def createGame(gameId, board, hands, cpus):
  game = GameRecord(gameId = gameId, board = str(board), hands = hands, cpus = cpus)
  game.put()

def updateGame(gameId, board, hands, cpus):
  qry = GameRecord.query(GameRecord.gameId == gameId)
  result = qry.fetch(10)
  if len(result) != 1:
    raise Exception('Faild to fetch game information.', str(len(result)))
  result[0].hands = [str(tile) for tile in hands]
  for cpu in cpus:
    for i in range(len(cpu)):
      if board.isAddable(cpu[i]):
        try:
          board.add(True, cpu[i])
        except Exception, e:
          board.add(False, cpu[i])
        cpu.pop(i)
        break
  result[0].board = str(board)
  result[0].cpus = [[str(tile) for tile in cpu] for cpu in cpus]
  result[0].put()

class MainPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = {
          'tilepool': 'Start a new game!',
          'tile_in_hands': [],
        }
        gameId = self.request.get('gameId')
        if gameId != '':
          board, hands, cpus = retriveGame(gameId)
          template_values['tilepool'] = unicode(board)
          template_values['tile_in_hands'] = [unicode(t) for t in hands]

        self.response.write(template.render(template_values))

class API(webapp2.RequestHandler):
    def get(self):
        action = str(self.request.get('action'))
        print self.request.get_range('isLeft')
        if action == 'deal':
          gameId = self.request.get('gameId') # uuid
          isLeft = bool(self.request.get_range('isLeft'))
          tileId = self.request.get_range('tileId')
          board, hands, cpus = retriveGame(gameId)
          try:
            board.add(isLeft, hands[tileId])
            pass
          except Exception, e:
            self.response.write('error')
          else:
            hands.pop(tileId)
            updateGame(gameId, board, hands, cpus)
            self.response.write(unicode(board))
        elif action == 'show':
          gameId = self.request.get('gameId')
          board, hands, cpus = retriveGame(gameId)
          self.response.write(unicode(board) + unicode(hands))
        elif action == 'start':
          # this needs to be rewritten after testing is done.
          board = Board()
          gameId = str(uuid.uuid1())
          playersHands = shuffleTiles(4)
          hands = [str(tile) for tile in playersHands[0]]
          playersHands.pop(0)
          cpus = [[str(tile) for tile in cpu] for cpu in playersHands]
          createGame(gameId, board, hands, cpus)
          self.response.write(gameId + ' ' + str(board))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/API', API)
], debug=True)

