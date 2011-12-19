import websocket
import asyncore
import json
import logging
import traceback

logger = logging.getLogger()
fileHandler = logging.FileHandler('ai.log')
fileHandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)

dirVec = ((-1, 0), (0, -1), (1, 0), (0, 1))

class AIBase:
    def __init__(self, name):
        self.name = name
        self.lastRoundId = -1
        self.added = False
        self.needAdd = True

    def getDirs(self, d):
        return filter(lambda x: abs(x-d)!=2, range(4)) 

    def newRound(self, roundId):
        return

    def addMe(self, type='python'):
        if not self.needAdd:
            return
        else:
            self.needAdd = False
        self.send({'op' : 'add',
                  'name': self.name,
                  'type': type})
	self.send({'op': 'info'})

    def turn(self, d):
        self.send({'op': 'turn',
                   'direction': d,
                   'round': -1})

    def sprint(self):
        self.send({'op' : 'sprint'})

    def setIndex(self, idx):
        print "My Index:", idx
        self.added = True
        self.idx = idx

    def setSender(self, sender):
        self.send = sender

    def onUpdateMap(self):
        return

    def setMap(self, size, walls, portals):
        self.w = size[0]
        self.h = size[1]
        self.walls = walls
        self.portals = portals
        self.onUpdateMap()

    def setStatus(self, data):
        if data['status'] == 'finished':
            self.added = False
            self.needAdd = True
            return
        if not self.added:
            self.addMe()
        self.eggs = data['eggs']
        self.gems = data['gems']
        self.snakes = data['snakes']
        print self.lastRoundId, data['round']
        if data['round'] != self.lastRoundId:
            self.lastRoundId = data['round']
            if self.added:
                try:
                    self.newRound(self.lastRoundId)
                except:
                    traceback.print_exc()
                    
        

class EventHandler:
    def __init__(self, url, room, ai):
        self.room = room
        self.ai = ai
        self.id = ""
        ai.setSender(self.aiSend)

    def send(self, data):
        self.sock.send(data)
   
    def aiSend(self, data):
        data['id'] = self.id
	data['room'] = self.room
	print "ai-send:", data
        return self.send(json.dumps(data))
    
    def onopen(self, ws):
        logger.info("connected, now send init info")
        self.send(json.dumps({'op': 'setroom', 'room': self.room}))
        self.send(json.dumps({'op': 'map', 'room': self.room}))
        self.send(json.dumps({'op': 'info', 'room': self.room}))

    def onmessage(self, ws, m):
        data = json.loads(str(m))
        if data['op']=='info':
            self.ai.setStatus(data)
        elif data['op']=='add':
            if 'status' in data:
                raise Exception(data['status'])
            self.ai.setIndex(data['seq'])
            self.id = data['id']
        elif data['op']=='map':
            self.ai.setMap(data['size'], data['walls'], data['portals'])
        else:
            logger.info("recv: " + str(data))


def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def startGame(url, room, ai):
#    websocket.enableTrace(True)
    handler = EventHandler(url, room, ai)
    sock = websocket.WebSocketApp(url, on_message = handler.onmessage,
                                  on_error = on_error,
                                  on_close = on_close)
    sock.on_open = handler.onopen
    handler.sock = sock
    sock.run_forever()

