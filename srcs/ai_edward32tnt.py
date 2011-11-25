#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: ai_edward32tnt
"""
from ailib import *

LEFT, UP, RIGHT, DOWN = range(4)
class AI(BaseAI):
    def __init__(self):
        self.name = 'edward32tnt ai %d' % random.randint(1, 1000)
        types = ['python', 'ruby']
        self.type = types[random.randint(0, 1)]

    def setmap(self, map):
        self.map = map

    def get_nearest_bean(self, beans, head):
        bean, distance = None, None
        for b in beans:
            d = abs(head[0] - b[0]) ** 2 + \
                abs(head[1] - b[1]) ** 2
            if not bean or d < distance:
                bean = b
                distance = d
        return bean
        
    def step(self, info):
        """
        caculate next direction by use rating
        """
        self.info = info
        result =  self.cmd_turn()
        return result

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
        res = []
        for w in self.map['walls']:
            res.append(w)
        return res
    
    def set_food(self):
        res = []
        if self.type == 'python':
            food = 'eggs'
        else:
            food = 'gems'
        for e in self.info[food]:
            if [x for x in self.get_around(e, steps=2) if x in self.other_head]: continue
            res.append(e)
        return res
    
    def set_posion(self):
        res = []
        if self.type != 'python':
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
        self.head = self.info['snakes'][self.seq]['body'][0]
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
        return direction

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


# Version 1.1
#
# Changes in 1.1: 
# In order to optimize the list handling I implemented the location id (lid) attribute.
# This will make the all list serahces to become extremely more optimized.

class Path:
    def __init__(self,nodes, totalCost):
        self.nodes = nodes;
        self.totalCost = totalCost;

    def getNodes(self): 
        return self.nodes    

    def getTotalMoveCost(self):
        return self.totalCost

class Node:
    def __init__(self,location,mCost,lid,parent=None):
        self.location = location # where is this node located
        self.mCost = mCost # total move cost to reach this node
        self.parent = parent # parent node
        self.score = 0 # calculated score for this node
        self.lid = lid # set the location id - unique for each location in the map

    def __eq__(self, n):
        if n.lid == self.lid:
            return 1
        else:
            return 0


class AStar:

    def __init__(self,maphandler):
        self.mh = maphandler
                
    def _getBestOpenNode(self):
        bestNode = None        
        for n in self.on:
            if not bestNode:
                bestNode = n
            else:
                if n.score<=bestNode.score:
                    bestNode = n
        return bestNode

    def _tracePath(self,n):
        nodes = [];
        totalCost = n.mCost;
        p = n.parent;
        nodes.insert(0,n);       
        
        while 1:
            if p.parent is None: 
                break

            nodes.insert(0,p)
            p=p.parent
        
        return Path(nodes,totalCost)

    def _handleNode(self,node,end):        
        i = self.o.index(node.lid)
        self.on.pop(i)
        self.o.pop(i)
        self.c.append(node.lid)

        nodes = self.mh.getAdjacentNodes(node,end)
                   
        for n in nodes:
            if n.location.x % self.mh.w == end.x and n.location.y % self.mh.h == end.y:
                # reached the destination
                return n
            elif n.lid in self.c:
                # already in close, skip this
                continue
            elif n.lid in self.o:
                # already in open, check if better score
                i = self.o.index(n.lid)
                on = self.on[i];
                if n.mCost<on.mCost:
                    self.on.pop(i);
                    self.o.pop(i);
                    self.on.append(n);
                    self.o.append(n.lid);
            else:
                # new node, append to open list
                self.on.append(n);                
                self.o.append(n.lid);

        return None

    def findPath(self,fromlocation, tolocation):
        self.o = []
        self.on = []
        self.c = []

        end = tolocation
        fnode = self.mh.getNode(fromlocation)
        self.on.append(fnode)
        self.o.append(fnode.lid)
        nextNode = fnode 
               
        while nextNode is not None: 
            finish = self._handleNode(nextNode,end)
            if finish:                
                return self._tracePath(finish)
            nextNode=self._getBestOpenNode()
                
        return None
      
class SQ_Location:
    """A simple Square Map Location implementation"""
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __eq__(self, l):
        """MUST BE IMPLEMENTED"""
        if l.x == self.x and l.y == self.y:
            return 1
        else:
            return 0

class SQ_MapHandler:
    """A simple Square Map implementation"""

    def __init__(self,mapdata,width,height):
        self.m = mapdata
        self.w = width
        self.h = height

    def getNode(self, location):
        """MUST BE IMPLEMENTED"""
        x = location.x
        y = location.y
        if x<0 or x>=self.w or y<0 or y>=self.h:
            #return None
            x = x % self.w
            y = y % self.h
            
        d = self.m[(y*self.w)+x]
        if d == -1:
            return None

        return Node(location,d,((y*self.w)+x));                

    def getAdjacentNodes(self, curnode, dest):
        """MUST BE IMPLEMENTED"""        
        result = []
       
        cl = curnode.location
        dl = dest
        
        n = self._handleNode(cl.x+1,cl.y,curnode,dl.x,dl.y)
        if n: result.append(n)
        n = self._handleNode(cl.x-1,cl.y,curnode,dl.x,dl.y)
        if n: result.append(n)
        n = self._handleNode(cl.x,cl.y+1,curnode,dl.x,dl.y)
        if n: result.append(n)
        n = self._handleNode(cl.x,cl.y-1,curnode,dl.x,dl.y)
        if n: result.append(n)
                
        return result

    def _handleNode(self,x,y,fromnode,destx,desty):
        n = self.getNode(SQ_Location(x,y))
        if n is not None:
            dx = min(abs(x - destx), self.w - abs(x-destx))
            dy = min(abs(y - desty), self.h - abs(y-desty))
            emCost = dx+dy
            n.mCost += fromnode.mCost                                   
            n.score = n.mCost+emCost
            n.parent=fromnode
            return n

        return None    
        

if __name__=="__main__":
    cmd_run(AI)
