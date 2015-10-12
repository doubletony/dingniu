import jinja2
import json
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
  players = ndb.StructuredProperty(PlayerRecord, repeated=True)

def retriveGame(gameId):
  qry = GameRecord.query(GameRecord.gameId == gameId)
  result = qry.fetch(10)
  if len(result) != 1:
    raise Exception('Faild to fetch game information.', str(len(result)))
  board = parseBoard(result[0].board)
  players = [parsePlayerRecord(cpu) for cpu in result[0].players]
  return board, players[0], players[1:]

def createGame(gameId, board, allhands):
  players = []
  for i in range(len(allhands)):
    hands = allhands[i]
    players.append(PlayerRecord(name='CPU' + str(i + 1), hands = hands, discards = []))
  players[0].name = 'player'
  game = GameRecord(gameId = gameId, board = str(board), players = players)
  game.put()

def updateGame(gameId, board, player, competitors):
  qry = GameRecord.query(GameRecord.gameId == gameId)
  result = qry.fetch(10)
  if len(result) != 1:
    raise Exception('Faild to fetch game information.', str(len(result)))
  result[0].players[0].hands = [str(tile) for tile in player.hands]
  result[0].players[0].discards = [str(tile) for tile in player.discards]
  for cpu in competitors:
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
  for i in range(len(competitors)):
    cpu = result[0].players[i + 1]
    cpu.hands = [str(tile) for tile in competitors[i].hands]
    cpu.discards = [str(tile) for tile in competitors[i].discards]
  result[0].put()

def getGameResults(players):
  points = []
  result = ''
  for player in players:
    point = player.getTotalPoints()
    tiles = player.getDiscardedTiles()
    points.append(point)

  min_point = min(points)
  max_point = max(points)
  if min_point == max_point:
    return 'Draw! Everyone is winner!'
  total_award = 0
  BIG_PENALTY = 2
  SMALL_PENALTY = 1
  winner_count = 0
  # Calculate the award amount
  for player in players:
    point = player.getTotalPoints()
    if point == max_point:
      total_award += BIG_PENALTY
    elif point > min_point:
      total_award += SMALL_PENALTY
    else:
      # winner
      winner_count += 1

  # Assign the awards and penalty
  for player in players:
    point = player.getTotalPoints()
    if point == max_point:
      result = result + player.name + ' loses $ ' + str(BIG_PENALTY) + ' Discard: ' + str(point) + ' points. ' + str([str(tile) for tile in player.discards]) + '\n'
    elif point > min_point:
      result = result + player.name + ' loses $ ' + str(SMALL_PENALTY) + ' Discard: ' + str(point) + ' points. ' + str([str(tile) for tile in player.discards]) + '\n'
    else:
      # winner
      result = result + player.name + ' wins $ ' + str(total_award * 1.0 / winner_count) + ' Discard: ' + str(point) + ' points. ' + str([str(tile) for tile in player.discards]) + '\n'
  return result

DEPLOY_FOR_MOBILE = False

def display(item):
  return str(item) if DEPLOY_FOR_MOBILE else unicode(item)

class MainPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = {
          'tilepool': 'Start a new game!',
          'tile_in_hands': [],
          'mobileSite': DEPLOY_FOR_MOBILE,
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
          self.response.headers['Content-Type'] = 'application/json'
          responseObj = {}
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
            responseObj['board'] = display(board)
            print "player hands:", len(player.hands)
            if len(player.hands) == 0:
              responseObj['result'] = getGameResults([player] + players)
              print responseObj['result']
            self.response.write(json.dumps(responseObj))
        elif action == 'show':
          gameId = self.request.get('gameId')
          board, player, players = retriveGame(gameId)
          self.response.write(display(board) + display(player.hands))
        elif action == 'start':
          # this needs to be rewritten after testing is done.
          board = Board()
          gameId = str(uuid.uuid1())
          playersHands = shuffleTiles(4)
          allhands = [[str(tile) for tile in hands] for hands in playersHands]
          createGame(gameId, board, allhands)
          self.response.write(gameId + ' ' + str(board))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/API', API)
], debug=True)

