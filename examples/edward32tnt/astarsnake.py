#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: random snake
用来作为示例代码
"""
import json, time, random, sys
import urllib, httplib
from AStar import AStar, SQ_MapHandler, SQ_Location

LEFT, UP, RIGHT, DOWN = range(4)
class RandomSnake():
    def __init__(self, room=0, mytype='python'):
        # 建立web连接
        self.conn = httplib.HTTPConnection('pythonvsruby.org')#"192.168.1.106")#"localhost:4567") 
        #self.conn = httplib.HTTPConnection("192.168.1.106")
	self.room = room
	self.mytype = mytype

    def post(self, cmd, data):
        """
        发送命令给服务器
        """
        self.conn.request("POST", '/room/%s/%s' % (self.room, cmd),
                          urllib.urlencode(data))
        result = self.conn.getresponse().read()
        return json.loads(result)

    def get(self, cmd):
        """
        获取信息
        """
        self.conn.request("GET", '/room/%s/%s' % (self.room, cmd))
        result = self.conn.getresponse().read()
        return json.loads(result)
    
    def cmd_add(self):
        """
        添加新的蛇
        """
        result = self.post("add",
                           dict(name = "astar test",
                                type = self.mytype))
        self.me, self.info = result[0], result[1]
        return self.me, self.info

############ 取得地图信息

    # 猜测敌人头附近的问题    
    def set_guess_posion(self):
        res = []
        for snake in self.info['snakes']:
            if self.head != snake['body'][0]:
                for point in self.get_around(snake['body'][0]):
                    res.append(point)
        return res       

            
    def set_others(self):
        self.other_head = []
        res = []
        for snake in self.info['snakes']:
            for body in snake['body']:
                res.append(body)
            if self.head != snake['body'][0]:
                self.other_head.append(snake['body'][0])
        return res
    
    def set_walls(self):
        self.cmd_map()
        res = []
        for w in self.map['walls']:
            res.append(w)
        return res
    
    def set_food(self):
        res = []
        if self.mytype == 'python':
            food = 'eggs'
        else:
            food = 'gems'
        for e in self.info[food]:
            if [x for x in self.get_around(e, steps=2) if x in self.other_head]: continue
            res.append(e)
        return res
    
    def set_posion(self):
        res = []
        if self.mytype != 'python':
            posion = 'eggs'
        else:
            posion = 'gems'
        for g in self.info[posion]:
            res.append(g)
        return res

    ###########    

    
    def cmd_turn(self):
        """
        控制蛇方向
        """
        direction = None
        self.head = self.info['snakes'][self.me['seq']]['body'][0]
        others = self.set_others()
        walls = self.set_walls()
        food = self.set_food()
        posion = self.set_posion()
        guess_posion = self.set_guess_posion()

        mapx, mapy = self.map['size']
        startpoint = self.head


        # 第一次尝试绝对安全路线。
        # 如果没有路线，则尝试不安全路线。
        next = self.find_safe_path(startpoint, food, others, walls, posion, guess_posion)
        if next:
            direction = self.find_next_direction_by_point(self.head, next)
        else:
            next = self.find_no_safe_path(startpoint, food, others, walls)
            if next:
                direction = self.find_next_direction_by_point(self.head, next)
        #print mapdata[-mapx:]
        #print mapdata[-mapx:]
        #print mapw
        #print maph
        #print startpoint
        #print endpoint
            
        # 再没有路线则朝尾部方向寻找
        if direction is None:
            # 暂时先寻找自己尾部的方向移动拜托被围的问题
            if not food: 
                direction = random.randint(0, 3)
            else:
                direction = self.find_next_direction_by_point(self.head, self.info['snakes'][self.me['seq']]['body'][-1])
        result = self.post("turn",
                           dict(id = self.me["id"],
                                round = self.info["round"],
                                direction = direction))
        self.turn, self.info = result[0], result[1]

################# 工具类可以转移出去
    def find_safe_path(self, startpoint, food, others, walls, posion, guess_posion):
        return self._get_path(startpoint, food, others, walls, posion, guess_posion)

    def find_no_safe_path(self, startpoint, food, others, walls):
        return self._get_path(startpoint, food, others, walls)
        
    def _get_path(self, startpoint, food, others, walls, posion=[], guess_posion=[]):
        counts = 0
        next = None
        for e in food:
            endpoint = e
            mapdata = []
            for y in range(self.map['size'][1]):
                for x in range(self.map['size'][0]):
                    rc = [x, y]
                    if rc == self.head:
                        mapdata.append(5)
                        continue
                    if rc == endpoint:
                        mapdata.append(6)
                        continue
                    if rc in others or rc in walls or rc in posion or rc in guess_posion:
                        mapdata.append(-1)
                        continue
                    mapdata.append(1)

            astar = AStar(SQ_MapHandler(mapdata, self.map['size'][0], self.map['size'][1]))
            start = SQ_Location(startpoint[0], startpoint[1])
            end = SQ_Location(endpoint[0], endpoint[1])
            
            p = astar.findPath(start, end)
            if not p:continue
            if len(p.nodes) < counts or next == None:
                counts = len(p.nodes)
                next = [p.nodes[0].location.x , p.nodes[0].location.y]
        return next 

    def find_next_direction_by_point(self, point, next):
        if point[0] < next[0]: return RIGHT
        if point[0] > next[0]: return LEFT
        if point[1] > next[1]: return UP
        if point[1] < next[1]: return DOWN

    def find_next_point_by_direction(self, point, direction, step):
        if direction == LEFT: return [point[0] - step, point[1]]
        if direction == RIGHT: return [point[0] + step, point[1]]
        if direction == UP: return [point[0], point[1] - step]
        if direction == DOWN: return [point[0], point[1] + step]
        
    def get_around(self, point, steps=1):
        for step in range(steps):
            for d in (LEFT, UP, RIGHT, DOWN):
                yield self.find_next_point_by_direction(point, d, step+1)

##############        ############

            
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

def main(argv):
    room = '0'
    snake_type = 'python'
    if len(argv) > 2:
        room = argv[1]
        snake_type = argv[2]
    
    rs = RandomSnake(room=room, mytype=snake_type)

    rs.cmd_add()
    while True:
        rs.cmd_turn()
    
if __name__=="__main__":
    main(sys.argv)


