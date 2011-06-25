#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: map
"""
import random
from game import *

class Map:
    walltoken = ['.','W','S']
    # nydus tokens
    nydustoken = ['A','B','C','D','E']

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
        ret = self.ommitComment(data[pt].strip())
        if ret == '': return pt+1
        ret = ret.split(':')
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
        elif ret[0] == 'food':
            self.meta['food'] = int(ret[1])
            self.beangen.maxbean = self.meta['food']
        elif ret[0] in ['author','version','name','snakelength','maxfoodvalue']:
            self.meta[ret[0]] = ret[1]
        return pt+1
        
    def parseMap(self, data, pt):
        self.walls = []
        #self.beans = []
        self.snakes = []
        self.nydus = {}
        
        for y in range(self.meta['height']):
            for x in range(self.meta['width']):
                v = data[pt+y][x]
                if v == 'W':
                    self.walls.append([x,y])
                #elif v == 'X':
                #    self.beans.append([x,y])
                elif v == 'S':
                    self.snakes.append([x,y])
                elif v in self.nydustoken:
                    idx = nydustoken.index(v)
                    if idx in self.nydus.keys():
                        self.nydus[2*idx+1] = [x,y]
                    else:
                        self.nydus[2*idx] = [x,y]
        
        self.nydus = list(self.nydus)
        return pt + self.meta['height']
        
    def ommitComment(self, str):
        sharp = str.find('#')
        if sharp >0:
            return str[:sharp]
        return str

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
        self.maxbean = 1
        
    def can(self, ctx):
        return ctx.status == 'running' and (self.canEgg(ctx) or self.canGem(ctx))
        #return ctx.round % 4 == 0 and ctx.status == 'running'
    def gen(self, ctx):
        gems,eggs = [],[]
        needgem, needegg = self.maxbean - len(ctx.gems), self.maxbean - len(ctx.eggs)
        
        while needgem>0:
            gem = self.randomGen(ctx, gems)
            gems.append(gem)
            needgem -= 1
        
        while needegg>0:
            egg = self.randomGen(ctx, gems + eggs)
            eggs.append(egg)
            needegg -= 1
        
        return [eggs,gems]
    
    def canEgg(self, ctx):
        return len(ctx.eggs)<self.maxbean
    def canGem(self, ctx):
        return len(ctx.gems)<self.maxbean
    def randomGen(self, ctx, ban):
        beanx = range(0, self.map.meta['width'])
        random.shuffle(beanx)
        for x in beanx:
            beany = range(0, self.map.meta['height'])
            random.shuffle(beany)
            for y in beany:
                if not ctx.check_hit([x,y]) and not [x,y] in ban:
                    return [x,y]
            
        
        
        
