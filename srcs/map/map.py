#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: map
"""
import random, yaml, json
from game import *

class Map:
    walltoken = ['.','W','S']
    # nydus tokens
    portal_token = ['A','B','C','D','E']

    def __init__(self):
        self.beangen = MapBeanGen(self)
        self.wallgen = MapWallGen(self)
        self.meta = {}

    @staticmethod
    def loadfile(filename):
        data = yaml.load(open(filename).read())
        return Map.loaddata(data)

    @staticmethod
    def loaddata(data):
        map = Map()
        map.load(data)
        return map
    
    def load(self, data):
        self.meta = data
        self.beangen.maxbean = self.meta['food']

        self.walls = []
        self.snakes = []
        self.portals = []
        
        data = data['map'].strip().split('\n')

        for y in range(self.meta['height']):
            for x in range(self.meta['width']):
                v = data[y][x]
                if v == 'W':
                    self.walls.append([x,y])
                #elif v == 'X':
                #    self.beans.append([x,y])
                elif v == 'S':
                    self.snakes.append([x,y])
                    
                elif v in self.portal_token:
                    idx = self.portal_token.index(v)
                    shortage = (idx+1)*2 - len(self.portals)
                    if shortage > 0:
                        self.portals.extend([None] * shortage)
                    if self.portals[2*idx]:
                        self.portals[2*idx+1] = [x,y]
                    else:
                        self.portals[2*idx] = [x,y]


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
            
        
        
        
