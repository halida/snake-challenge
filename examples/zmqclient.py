#!/usr/bin/env python -u
#-*- coding:utf-8 -*-
"""
module: interactive with server
"""
import logging, sys, json, time, os
import zmq, traceback

VERSION = '20110401'
LOG_FILE = 'zmqclient.log'
SERVER = 'pythonvsruby.org'

class ZmqClient():
    
    def __init__(self, room, player):
        context = zmq.Context()
        self.suber = context.socket(zmq.SUB)
        self.suber.connect('ipc:///tmp/game_puber.ipc')
        self.suber.setsockopt(zmq.SUBSCRIBE, 'room:%s '%room)
        self.oper = context.socket(zmq.REQ)
        self.oper.connect('ipc:///tmp/game_oper.ipc')
        self.room = room
        self.player = player
        self.token = None
        self.seq = None
        self.lastround = 0
        
    def op(self, op, kw=None):
        if not kw: kw = dict()
        kw['op'] = op
        kw['room'] = int(self.room)
        self.oper.send(json.dumps(kw))
        return json.loads(self.oper.recv())

    def add(self):
        """
        try add your player to platform
        """
        ret = self.op(
            'add', dict(name=self.player.name,
                        type=self.player.type))        
        if 'id' in ret.keys():
            self.token = ret['id']
            self.seq = int(ret['seq'])
            self.player.init(ret['seq'], self.op('map'))
        else:
            raise Exception(ret['status'])

    def info(self):
        info = self.suber.recv()
        info = info[info.index(' '):]
        return json.loads(info)
        
    def turnwrap(self, igore = False):
        try:
            return self.turn()
        except:
            if not igore:
                raise
            else:
                return True
                
    def turn(self):
        """
        try post your turn operation to platform
        """
        info = self.info()
        round = int(info['round'])
        
        if not info['snakes'][self.seq]['alive']:
            return False
        elif info['status'] == 'running':
            if round>self.lastround:
                op = self.player.turn(info)
                ret = self.op(
                        'turn', dict(id=self.token,
                         direction=op,
                         round=round))
                if 'status' not in ret.keys():
                    raise Exception("turn result error")
                elif ret['status'] == 'noid':
                    raise Exception(ret['status'])
                else:
                    self.lastround = round
                    print round,
                    return True
            else: return True
        elif info['status'] == 'waitplayer':
            return True
        elif info['status'] == 'finished':
            return False
        else:
            raise Exception("unrecognized status: %s" % info['status'])

if __name__ == '__main__':
    logging.basicConfig(filename = LOG_FILE, level = logging.INFO)
    
    try:
        exec "from "+sys.argv[1]+" import Player"
        
        if 'exception' in sys.argv:
            exception = True
            sys.argv.remove('exception')
        else:
            exception = False
        if 'debug' in sys.argv:
            debug = True
            sys.argv.remove('debug')
        else:
            debug = False
            
        if len(sys.argv)>2: room = sys.argv[2]
        else: room = '0'
        
        #unbuffered stdout
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        
        client = ZmqClient(room, Player(debug))
        
        client.add()
        print 'running',
        while client.turnwrap(exception):
            print '.',
            time.sleep(0.1)
        
        print
        print 'game finished'
        
    except Exception as e:
        logging.exception(e)
        print "client failed, please check client.log"