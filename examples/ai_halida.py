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
        self.type = types[random.randint(0, 1)]
        self.SPRINT = random.random() > 0.5
        self.count = 0
        self.round = -1

    def setmap(self, map):
        self.map = map

    def get_nearest_bean(self, beans, h, size):
        r_bean, r_dis, r_dir = None, None, None
        
        for b in beans:
            dis, dir = get_distance(b, h, size)
            
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
        size = self.map['size']
        self_snake = info['snakes'][self.seq]
        head = self_snake['body'][0]
        w, h = self.map['size']
        dirs = get_dirs(self_snake['body'])

        # not check when cannot move
        if self_snake['sprint'] < 0:
            return {'op': 'turn', 'direction': 0}
        
        if self.type == 'python':
            target_beans, nontarget_beans = info['eggs'], info['gems']
        else:
            target_beans, nontarget_beans = info['gems'], info['eggs']
            
        # find the nearest bean, and target direction
        nearest_bean, bean_direction = self.get_nearest_bean(target_beans, head, size)

        # rating for each direction
        ratings = [0, ] * len(dirs)
        
        # sprint when torgeting bean and nears!
        if ( self.SPRINT and
             nearest_bean and 
             ((head[0] == nearest_bean[0] and self_snake['direction'] in (1, 3) and abs(head[1] - nearest_bean[1]) < 15) or
              (head[1] == nearest_bean[1] and self_snake['direction'] in (0, 2) and abs(head[0] - nearest_bean[0]) < 15)
              ) and
             not any([self.check_hit(n)
                      for n in get_nexts(6, head, DIRECT[self_snake['direction']], size)])
             ):
            # print get_nexts(6, head, d, size)
            # print [self.check_hit(n)
            #        for n in get_nexts(6, head, DIRECT[self_snake['direction']], size)]
            return {'op': 'sprint'}
                
        for i, d in enumerate(dirs):
            # it is good if targeting a bean
            if nearest_bean:
                if d[0] == bean_direction[0]: ratings[i] += 2
                if d[1] == bean_direction[1]: ratings[i] += 2

            # find next positon
            next = get_next(head, d, size)

            # it is bad to hit a target
            if self.check_hit(next):
                ratings[i] = -10
                continue

            # sprint check!
            if (self_snake['sprint'] > 1 and
                any([self.check_hit(n)
                     for n in get_nexts(2, next, d, size)])):
                print get_nexts(6, head, d, size)
                print [self.check_hit(n)
                       for n in get_nexts(6, head, d, size)]
                ratings[i] = -10
                continue

            # bad to near other snakes head
            for s in info['snakes']:
                if s == self_snake: continue
                if near(next, s['body'][0], size):
                    ratings[i] = -2
                    continue

            # bad to eat other types of bean
            if next in nontarget_beans: ratings[i] -= 2

            # bad to near too many walls
            # near_walls = sum([near(next, w, size)
            #                   for w in self.map['walls']])
            # ratings[i] -= near_walls

        # return the best direction
        d = max(zip(ratings, dirs), key=lambda x: x[0])[1]
        return {'op': 'turn', 'direction': DIRECT.index(d)}

    
if __name__=="__main__":
    cmd_run(AI)
