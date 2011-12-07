#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: simple snake
用来作为示例代码
"""
import json, time
import urllib, httplib, logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

DIRS = [[-1, 0], [0, -1], [1, 0], [0, 1]]

class SimpleSnake():
    def __init__(self):
        self.conn = httplib.HTTPConnection("localhost", 9999)
        self.room = 0
        self.d = 0

    def cmd(self, cmd, data={}):
        """
        发送命令给服务器
        """
        data['op'] = cmd
        data['room'] = self.room
        # logging.debug('post: %s : %s', cmd, data)
        self.conn.request("POST", '/cmd',
                          urllib.urlencode(data),
                          {'Content-Type': 'application/x-www-form-urlencoded'})
        result = self.conn.getresponse().read()
        return json.loads(result)

    def cmd_add(self):
        self.me = self.cmd("add",
                           dict(name = "SimplePython",
                                type = "python"))
        return self.me
    
    def cmd_map(self):
        self.map = self.cmd("map")

    def cmd_info(self):
        self.info = self.cmd("info")

    def cmd_turn(self, dir):
        return self.cmd("turn",
                        dict(id = self.me["id"],
                             round = -1,
                             direction = dir))

    def step(self):
        snake = self.info['snakes'][self.me["seq"]]
        head = snake['body'][0]
        dir = DIRS[self.d]
        nexts = [
            [head[0] + dir[0]*i,
             head[1] + dir[1]*i]
            for i in [1,2,3,4]
            ]
    
        blocks = []
        blocks += self.map['walls']
        for snake in self.info['snakes']:
            blocks += snake['body']
    
        # change direction when there is block ahead
        for n in nexts:
            for b in blocks:
                if b[0] == n[0] and b[1] == n[1]:
                    self.d = (self.d + 1) % 4
                    return self.d
          
        return self.d


def main():
    rs = SimpleSnake()
    rs.cmd_map()
    logging.debug(rs.cmd_add())
    while True:
        time.sleep(0.3)
        rs.cmd_info()
        logging.debug(rs.cmd_turn(rs.step()))
    
if __name__=="__main__":
    main()


