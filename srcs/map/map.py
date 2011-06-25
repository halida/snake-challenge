#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: map
"""
import random
from game import *

class Map:
    walltoken = ['.','W','X','S']

    def __init__(self):
        self.beangen = MapBeanGen(self)
        self.wallgen = MapWallGen(self)
        self.meta = {}
        
    @staticmethod
    def load(mapfile):
        map = Map()
        map.loadfile(mapfile)
        return map
    
    def loadfile(self, mapfile):
        self.meta = {}
        with open(mapfile, 'r') as f:
            data = f.readlines()
            
        pt, linelen = 0, len(data)
        while pt<linelen:
            pt = self.parse(data, pt)
    
    def parse(self, data, pt):
        ret = data[pt].strip().split(':')
        if len(ret)!=2: raise Exception('map parse fail')
        
        if ret[0] == 'map':
            return self.parseMap(data, pt+1)
        elif ret[0] == 'walls':
            pass # TODO
        elif ret[0] == 'beans':
            pass # TODO
        elif ret[0] == 'size':
            size = ret[1].strip().split('x')
            if len(size)!=2: raise Exception('map size parse fail')
            self.meta['width'] = int(size[0])
            self.meta['height'] = int(size[1])
        elif ret[0] in ['author','version','name','snake','snakelength']:
            self.meta[ret[0]] = ret[1]
        return pt+1
        
    def parseMap(self, data, pt):
        self.walls = []
        self.beans = []
        self.snakes = []
        
        for y in range(self.meta['height']):
            for x in range(self.meta['width']):
                v = data[pt+y][x]
                if v == 'W':
                    self.walls.append([x,y])
                elif v == 'X':
                    self.beans.append([x,y])
                elif v == 'S':
                    self.snakes.append([x,y])
        return pt + self.meta['height']

class MapWallGen:
    def __init__(self, map):
        self.map = map
        
    def can(self, ctx):
        return ctx.round == 0 and ctx.status == 'initial'
    def gen(self, ctx):
        return self.map.walls

class MapBeanGen(BeanGen):
    def __init__(self, map):
        self.map = map
        
    def can(self, ctx):
        return ctx.round % 4 == 0 and ctx.status == 'running'
    def gen(self, ctx):
        beans = []
        for b in self.map.beans:
            if not ctx.check_hit(b):
                beans.append(b)
        
        if len(beans) > 1:
            egg = random.choice(beans)
            beans.remove(egg)        
            gem = random.choice(beans)
            return [[egg],[gem]]
        else:
            return [[],[]]
        
        
