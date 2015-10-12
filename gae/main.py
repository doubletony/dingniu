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

def parseTiles(hands):
  tiles = []
  for tile in hands:
    if tile == '':
      continue
    tiles.append(parseTile(tile))
  return tiles

def parsePlayer(name, hands, discards):
  player = Player(name)
  player.setHands(parseTiles(hands))
  player.setDiscards(parseTiles(discards))
  return player

### Starts App Engine Code
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class PlayerRecord(ndb.Model):
  name = ndb.StringProperty(indexed=False)
  hands = ndb.JsonProperty(indexed=False)
  discards = ndb.JsonProperty(indexed=False)

def parsePlayerRecord(record):
  return parsePlayer(record.name, record.hands, record.discards)

class GameRecord(ndb.Model):
  gameId = ndb.StringProperty(indexed=True)
  board = ndb.StringProperty(indexed=False)
  player = ndb.StructuredProperty(PlayerRecord)
  players = ndb.StructuredProperty(PlayerRecord, repeated=True)

def retriveGame(gameId):
  qry = GameRecord.query(GameRecord.gameId == gameId)
  result = qry.fetch(10)
  if len(result) != 1:
    raise Exception('Faild to fetch game information.', str(len(result)))
  board = parseBoard(result[0].board)
  player = parsePlayerRecord(result[0].player)
  players = [parsePlayerRecord(cpu) for cpu in result[0].players]
  return board, player, players

def createGame(gameId, board, hands, cpus):
  player = PlayerRecord(name='player', hands = hands, discards = [])
  players = []
  for i in range(len(cpus)):
    cpu = cpus[i]
    players.append(PlayerRecord(name='CPU' + str(i + 1), hands = cpu, discards = []))
  game = GameRecord(gameId = gameId, board = str(board), player = player, players = players)
  game.put()

def updateGame(gameId, board, player, players):
  qry = GameRecord.query(GameRecord.gameId == gameId)
  result = qry.fetch(10)
  if len(result) != 1:
    raise Exception('Faild to fetch game information.', str(len(result)))
  result[0].player.hands = [str(tile) for tile in player.hands]
  result[0].player.discards = [str(tile) for tile in player.discards]
  for cpu in players:
    added = False
    for i in range(len(cpu.hands)):
      if board.isAddable(cpu.hands[i]):
        added = True
        try:
          board.add(True, cpu.hands[i])
        except Exception, e:
          board.add(False, cpu.hands[i])
        cpu.hands.pop(i)
        break
    if not added:
      cpu.discards.append(cpu.hands.pop(i))
  result[0].board = str(board)
  for i in range(len(result[0].players)):
    cpu = result[0].players[i]
    cpu.hands = [str(tile) for tile in players[i].hands]
    cpu.discards = [str(tile) for tile in players[i].discards]
  result[0].put()

def display(item):
  return str(item)

class MainPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = {
          'tilepool': 'Start a new game!',
          'tile_in_hands': [],
        }
        gameId = self.request.get('gameId')
        if gameId != '':
          board, player, players = retriveGame(gameId)
          template_values['tilepool'] = display(board)
          template_values['tile_in_hands'] = [display(t) for t in player.hands]
        self.response.write(template.render(template_values))

class API(webapp2.RequestHandler):
    def get(self):
        action = str(self.request.get('action'))
        print self.request.get_range('isLeft')
        if action == 'deal':
          gameId = self.request.get('gameId') # uuid
          isLeft = bool(self.request.get_range('isLeft'))
          tileId = self.request.get_range('tileId')
          board, player, players = retriveGame(gameId)
          isDiscard = bool(self.request.get_range('isDiscard'))
          try:
            if not isDiscard:
              board.add(isLeft, player.hands[tileId])
              player.hands.pop(tileId)
            else:
              player.discards.append(player.hands.pop(tileId))
          except Exception, e:
            self.response.write('error')
          else:
            updateGame(gameId, board, player, players)
            self.response.write(display(board))
        elif action == 'show':
          gameId = self.request.get('gameId')
          board, player, players = retriveGame(gameId)
          self.response.write(display(board) + display(player.hands))
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

