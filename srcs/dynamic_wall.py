#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: dynamic wall samples
"""

from snakec.game import *

class FanWallGen(WallGen):    
    freq = 2    # fan frequence
    flen = 4    # fan length
    
    # fan movement offest
    offset = [[(-1,0), (1,0), (0,-1), (0,1)], \
            [(-1, -1), (-1,1), (1,-1), (1,1)]]
    
    def can(self, ctx):
        return ctx.round % self.freq == 0
        
    def gen(self, ctx):
        ct = [ctx.size[0]/2, ctx.size[1]/2]
        walls = [ct]
        ang = (ctx.round / self.freq) % 2
        
        def move(pt, of):
            return [pt[0]+of[0], pt[1]+of[1]]

        for of in self.offset[ang]:
            pt = ct[:]
            for i in range(self.flen):
                pt = move(pt, of)
                walls.append(pt[:])
        
        return walls
            