#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: random snake
用来作为示例代码
"""
import json, time, random
import urllib, httplib, logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

class RandomSnake():
    def __init__(self):
        # 建立web连接
        self.conn = httplib.HTTPConnection("pythonvsruby.org")

    def post(self, cmd, data):
        """
        发送命令给服务器
        """
        logging.debug('post: %s : %s', cmd, data)
        self.conn.request("POST", '/room/1/%s' % cmd,
                          urllib.urlencode(data))
        result = self.conn.getresponse().read()
        return json.loads(result)

    def get(self, cmd):
        """
        获取信息
        """
        logging.debug('get: %s', cmd)
        self.conn.request("GET", '/room/1/%s' % cmd)
        result = self.conn.getresponse().read()
        return json.loads(result)
    
    def cmd_add(self):
        """
        添加新的蛇
        """
        result = self.post("add",
                           dict(name = "RandomPython",
                                type = "python"))
        self.me, self.info = result[0], result[1]
        return self.me, self.info
    
    def cmd_turn(self):
        """
        控制蛇方向
        """
        current_direction = self.info["snakes"]\
                            [self.me["seq"]]\
                            ["direction"]
        result = self.post("turn",
                           dict(id = self.me["id"],
                                round = self.info["round"],
                                direction = random.randint(0, 3)))
        self.turn, self.info = result[0], result[1]

    def cmd_map(self):
        """
        获取地图信息
        """
        self.map = self.get("map")

    def cmd_info(self):
        """
        获取实时场景信息
        """
        self.info = self.get("info")

def main():
    rs = RandomSnake()
    logging.debug(rs.cmd_add())
    while True:
        time.sleep(0.1)
        logging.debug(rs.cmd_turn())
    
if __name__=="__main__":
    main()


