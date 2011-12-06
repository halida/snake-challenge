#!/usr/bin/env python -u
#-*- coding:utf-8 -*-
"""
module: interactive with server
"""
import logging, sys, json, time, os
import httplib, urllib, traceback

VERSION = '20110401'
LOG_FILE = 'client.log' 
SERVER = 'pythonvsruby.org'

class Client():
    
    def __init__(self, room, player):
        self.conn = httplib.HTTPConnection(SERVER)
        self.base = '/room/%s' % room
        self.player = player
        self.token = None
        self.seq = None
        self.lastround = 0
        
    def post(self, cmd, data):
        self.conn.request('POST', '%s/%s' % (self.base, cmd),
                            urllib.urlencode(data))
        result = self.conn.getresponse().read()
        logging.debug(result)
        return json.loads(result)
    
    def get(self, cmd):
        self.conn.request('GET', '%s/%s' % (self.base, cmd))
        result = self.conn.getresponse().read()
        logging.debug(result)
        return json.loads(result)
                    
    def add(self):
        """
        try add your player to platform
        """
        ret = self.post('add',
                            dict(name = self.player.name,
                                type = self.player.type))[0]
        if 'id' in ret.keys():
            self.token = ret['id']
            self.seq = int(ret['seq'])
            self.player.init(ret['seq'], self.get('map'))
        else:
            raise Exception(ret['status'])
    
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
        info = self.get('info')
        round = int(info['round'])
        
        if not info['snakes'][self.seq]['alive']:
            return False
        elif info['status'] == 'running':
            if round>self.lastround:
                op = self.player.turn(info)
                ret = self.post('turn',
                                dict(id = self.token,
                                    round = info['round'],
                                    direction = op))[0]
                #print "op-%s"%op,
                if 'status' not in ret.keys():
                    raise Exception("turn result error")
                elif ret['status'] == 'noid':
                    raise Exception(ret['status'])
                else:
                    self.lastround = round
                    print round,
                    return True
            else: return True
        elif info['status'] == 'waitforplayer':
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
        
        client = Client(room, Player(debug))
        
        client.add()
        print 'running',
        while client.turnwrap(exception):
            print '.',
            time.sleep(0.2)
        
        print
        print 'game finished'
        
    except Exception as e:
        logging.exception(e)
        print "client failed, please check client.log"
