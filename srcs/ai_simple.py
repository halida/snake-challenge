#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: ai simple
a simple ai demo
"""
from ailib import *


class AI():
    def __init__(self):
        self.name = 'simple ai'
        types = ['python', 'ruby']
        self.type = types[random.randint(0, 1)]
        self.count = 0
        self.round = -1

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
        s = info['snakes'][self.seq]
        w, h = self.map['size']
        dirs = get_dirs(s['body'])
        # rating
        ps = [0, ] * len(dirs)

        # find the nearest bean
        if self.type == 'python':
            beans = info['eggs']
        else:
            beans = info['gems']
        head = s['body'][0]
        nearest_bean = self.get_nearest_bean(beans, head)
        if nearest_bean:
            dx = - cmp(head[0], nearest_bean[0])
            dy = - cmp(head[1], nearest_bean[1])

        # for each direction
        for i, d in enumerate(dirs):
            # it is good if targeting a bean
            if nearest_bean:
                if d[0] == dx:
                    ps[i] += 1
                if d[1] == dy:
                    ps[i] += 1
            # find next positon
            next = [head[0] + d[0],
                    head[1] + d[1]]
            # it is bad to hit a wall
            if next in self.map['walls']:
                ps[i] = -10
                continue
            # also bad to hit another snake
            for s in info['snakes']:
                if next in s['body']:
                    ps[i] = -10
                    continue
            # bad to eat other types of bean
            if self.type == 'python':
                not_hit = info['gems']
            else:
                not_hit = info['eggs']
            if next in not_hit:
                ps[i] = -1

        # return the best direction
        d = max(zip(ps, dirs), key=lambda x: x[0])[1]
        return DIRECT.index(d)

usage = """\
    $ ai_simple.py [connect type] [room number]
    connect type is in [web, zero]
        web means use Restful http API,
        zero means use zeromq.
"""

def main():
    from ailib import run_ai, WebController, ZeroController
    try:
        room = int(sys.argv[2])
    except:
        print usage
        
    if sys.argv[1] == 'web':
        C = WebController
    elif sys.argv[1] == 'zero':
        C = ZeroController
    else:
        print usage
    run_ai(AI(), C(room))
    
if __name__=="__main__":
    main()
