#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: server
"""
from lib import *

import zmq
from zmq.eventloop import ioloop, zmqstream
# hack
ioloop.install()

import tornado
import tornado.web, tornado.websocket


context = zmq.Context()

# 用来接受info更新
suber = context.socket(zmq.SUB)
suber.connect('ipc:///tmp/game_puber.ipc')
# self.suber.setsockopt(zmq.SUBSCRIBE, 'room:%d '%room)
suber.setsockopt(zmq.SUBSCRIBE, '')


# 用来与服务器交互
oper = context.socket(zmq.REQ)
oper.connect('ipc:///tmp/game_oper.ipc')


class ChatRoomWebSocket(tornado.websocket.WebSocketHandler):
    connects = []
    chats = {}
    SAVED_CHATS = 30
    def open(self):
        self.name = '???'
        self.room = "root"
        # 显示现在已经在的人
        if len(self.connects) > 0:
            current_ins = ', '.join([u"%s in : %s" % (c.name, c.room)
                                     for c in self.connects])
        else:
            current_ins = 'none'
        self.write_message('current in: \n' + current_ins)
            
        self.connects.append(self)
        
    def on_message(self, message):
        data = json.loads(message)
        if data.has_key('name'):
            self.name = data['name']
            self.room = data['room']            
            self.broadcast(self.room, '<em>%s</em> enters the room: <em>%s</em>' % (self.name, self.room))
            # write some history chats
            for chat in self.chats.get(self.room, []):
                self.write_message(chat)
            return
        else:
            self.broadcast(self.room, '<em>%s</em> says: %s' % (self.name, data['msg']) )

    def broadcast(self, room, msg):
        # save chat
        if not self.chats.has_key(room):
            self.chats[room] = []
        room_chats = self.chats[room]
        room_chats.append(msg)
        if len(room_chats) > self.SAVED_CHATS:
            self.chats[room] = room_chats[-self.SAVED_CHATS:]
        
        for c in self.connects:
            if c.room != room:
                continue
            try:
                c.write_message(msg)
            except Exception as e:
                logging.debug(str(e))
                try:
                    self.connects.remove(c)
                except:
                    pass
            
    def on_close(self):
        self.connects.remove(self)
        self.broadcast(self.room, self.name + ' leaves.')

class Cmd(tornado.web.RequestHandler):
    def post(self):
        data = self.request.arguments
        # warp list
        for key in data:
            data[key] = data[key][0]
        data = json.dumps(data)
        oper.send_unicode(data)
        result = oper.recv()
        self.set_header("Content-Type", "application/json")
        self.write(result)

class InfoWebSocket(tornado.websocket.WebSocketHandler):
    
    connects = []
    room = -1

    @classmethod
    def check_info(cls, data):
        # 拆分掉room头信息
        data = data[0]
        i = data.index(' ')
        room = int(data[:i].split(':')[1])
        # 发送给所有注册到这个room的连接
        cls.send_info(room, data[i:])

    @classmethod
    def send_info(cls, room, info):
        for c in cls.connects[:]:
            if c.room == room:
                try:
                    c.write_message(info)
                except:
                    try:
                        cls.remove(c)
                    except:
                        pass
            
    def open(self):
        self.connects.append(self)
        
    def on_message(self, message):
        data = json.loads(message)
        if data.get('op') == 'setroom':
            self.room = int(data['room'])
        else:
            self.process_cmd(message)

    def process_cmd(self, message):
        # logging.debug(message)
        oper.send_unicode(message)
        result = oper.recv()
        self.write_message(result)

    def on_close(self):
        try:
            self.connects.remove(self)
        except:
            pass

stream = zmqstream.ZMQStream(suber)
stream.on_recv(InfoWebSocket.check_info)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    # "login_url": "/login",
    # "xsrf_cookies": True,
    'debug' : True,
    # 'gzip' : True,
}

application = tornado.web.Application([
    (r"/info", InfoWebSocket),
    (r"/chatroom", ChatRoomWebSocket),
    (r"/cmd", Cmd),
    ], **settings)

def main():
    application.listen(9999)
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "bye!"

if __name__ == "__main__":
    main()
