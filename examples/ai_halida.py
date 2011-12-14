#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: ai simple
a simple ai demo
"""
from ailib import *

class AI(BaseAI):
    def __init__(self):
        self.name = 'simple ai %d' % random.randint(1, 1000)
        types = ['python', 'ruby']
        self.type = 'python'#types[random.randint(0, 1)]
        self.count = 0
        self.round = -1

    def setmap(self, map):
        self.map = map

    def get_nearest_bean(self, beans, h):
        r_bean, r_dis, r_dir = None, None, None
        
        for b in beans:
            dis, dir = get_distance(b, h, self.map['size'])
            
            if not r_bean or dis < r_dis:
                r_bean = b
                r_dis = dis
                r_dir = dir
                
        return r_bean, r_dir

    def check_hit(self, next):
        # it is bad to hit a wall
        if next in self.map['walls']:
            return True
        # also bad to hit another snake
        for s in self.info['snakes']:
            if next in s['body']:
                return True

    def step(self, info):
        """
        caculate next direction by use rating
        -10: wall, or hit
        x+1, y+1: target bean direction
        -1: not target bean 
        """
        self.info = info
        self_snake = info['snakes'][self.seq]
        head = self_snake['body'][0]
        w, h = self.map['size']
        dirs = get_dirs(self_snake['body'])
        
        if self.type == 'python':
            target_beans, nontarget_beans = info['eggs'], info['gems']
        else:
            target_beans, nontarget_beans = info['gems'], info['eggs']
            
        # find the nearest bean, and target direction
        nearest_bean, bean_direction = self.get_nearest_bean(target_beans, head)

        # rating for each direction
        ratings = [0, ] * len(dirs)
        
        for i, d in enumerate(dirs):

            # it is good if targeting a bean
            if nearest_bean:
                if d[0] == bean_direction[0]: ratings[i] += 1
                if d[1] == bean_direction[1]: ratings[i] += 1

            # find next positon
            next = [head[0] + d[0],
                    head[1] + d[1]]

            # it is bad to hit a target
            if self.check_hit(next):
                ratings[i] = -10
                continue

            # bad to near other snakes head
            for s in info['snakes']:
                if s == self_snake: continue
                if near(next, s['body'][0], self.map['size']):
                    ratings[i] = -2
                    continue
                
            # bad to eat other types of bean
            if next in nontarget_beans:
                ratings[i] = -1

        # return the best direction
        d = max(zip(ratings, dirs), key=lambda x: x[0])[1]
        return DIRECT.index(d)

    
if __name__=="__main__":
    cmd_run(AI)
