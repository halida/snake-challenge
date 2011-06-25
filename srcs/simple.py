#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: simple strategy for game
"""

from lib import *
from game import *

BEAN_TIME = 6

def simpleBeanGen(ctx):
    """
    随机获取一个空的位置
    可能是性能陷阱?
    """
    while True:
        p = [random.randint(0, ctx.w-1),
             random.randint(0, ctx.h-1)]
        # 不要和其他东西碰撞
        if ctx.check_hit(p):
            continue
        return p

class SimpleBeanGen(BeanGen):
    def can(self, ctx):
        return ctx.enable_bean and ctx.round % BEAN_TIME == 0
    def gen(self, ctx):
        ret = [[],[]]
        if self.canEgg(ctx):
            ret[0].append(simpleBeanGen(ctx))
        if self.canGem(ctx):
            ret[1].append(simpleBeanGen(ctx))
        if ret[0] == ret[1]:
            ret[random.randint(0,1)] = []
        return ret
        
    def canEgg(self, ctx):
        return len(ctx.eggs)<10
    def canGem(self, ctx):
        return len(ctx.gems)<10 
        
class SimpleWallGen(WallGen):
    def can(self, ctx):
        # in simple mode, only generate wall before game start
        return ctx.round == 0
    def gen(self, ctx):        
        # 因为js没有(), 只好用[]
        return [[10, i] for i in range(5, 35)]
    
