#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: server
"""
import sys, os, time, logging
import tornado.ioloop, tornado.web, tornado.websocket

import zmq
context = zmq.Context()
# 用来接受info更新
suber = context.socket(zmq.SUB)
suber.connect('ipc:///tmp/game_puber.ipc')
# self.suber.setsockopt(zmq.SUBSCRIBE, 'room:%d '%room)
suber.setsockopt(zmq.SUBSCRIBE, '')
# 用来与服务器交互
oper = context.socket(zmq.REQ)
oper.connect('ipc:///tmp/game_oper.ipc')


class InfoWebSocket(tornado.websocket.WebSocketHandler):
    connects = []
    room = -1

    @classmethod
    def check_info(cls):
        # 计划好下次更新
        cls.io_loop.add_timeout(time.time()+0.5,
                                InfoWebSocket.check_info)
        while True:
            # 检查是否有更新
            try:
                data = suber.recv(zmq.NOBLOCK)
                # 拆分掉room头信息
                i = data.index(' ')
                room = int(data[:i].split(':')[1])
                # print "on sub info: ", data
                # 发送给所有注册到这个room的连接
                cls.send_info(room, data[i:])
            except zmq.ZMQError:
                return
            
    @classmethod
    def send_info(cls, room, info):
        for c in cls.connects:
            if c.room == room:
                c.write_message(info)
            
    def open(self):
        self.connects.append(self)
        
    def on_message(self, message):
        print message
        if message.startswith('room:'):
            self.room = int(message[5:])
        else:
            self.process_cmd(message)

    def process_cmd(self, message):
        oper.send_unicode(message)
        result = oper.recv()
        print result
        self.write_message(result)

    def on_close(self):
        self.connects.remove(self)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    # "login_url": "/login",
    # "xsrf_cookies": True,
    'debug' : True,
}

application = tornado.web.Application([
    (r"/info", InfoWebSocket),
    ], **settings)

def main():
    application.listen(9999)
    try:
        io_loop = tornado.ioloop.IOLoop.instance()

        InfoWebSocket.io_loop = io_loop
        # 每隔若干时间, 检查有没有pub
        io_loop.add_timeout(time.time()+1, InfoWebSocket.check_info)
        
        io_loop.start()
    except KeyboardInterrupt:
        print "bye!"

if __name__ == "__main__":
    main()
