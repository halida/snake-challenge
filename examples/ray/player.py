#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: player
to run this player, use client.py for web or zmqclient.py for pygame mode
usage: python client.py ray.player <room> <ignore exception> <debug mode>
sample: 
1 python client.py ray.player 0 debug       # start player in room 0 in debug mode
2 python client.py ray.player 1 exception   # start player in room 1 in no-debug 
    and ignore exceptions mode
3 python client.py ray.player               # start player in room default room 0, no-debug,
    and allow exception thrown

"""
import random, os
import Image, ImageColor

class Player():
    offset = [(-1,0), (0,-1), (1,0), (0,1)]
    direction = {(-1,0):0, (0,-1):1, (1,0):2, (0,1):3}
    EMPTY, WALL, EGG, GEM, SNAKE = 0, 100, 40, 70, 10
    TYPE = [{'type':'python', 'bean':'eggs', 'beanw':EGG, 'opbean':'gems', 'opbeanw':GEM}, \
            {'type':'ruby', 'bean':'gems', 'beanw':GEM, 'opbean':'eggs', 'opbeanw':EGG}]
    TMP = 'ray/tmp'

    def __init__(self, debug=False):
        self.name = 'Ray Ling'
        self.typec = self.TYPE[0]
        self.type = self.typec['type']
        self.dead = []
        self.debug = debug
    
    def init(self, seq, map):
        self.seq = seq
        self.size = map['size']
        self.analmap = self.initmap(0)
        self.realmap = self.initmap(self.EMPTY)
        self.addwall(map['walls'], self.realmap, self.analmap) 
        # debug map
        if self.debug:
            if not os.path.exists(self.TMP):
                os.mkdir(self.TMP)
            #self.map2image(self.analmap, 'analmap', 100)
            self.map2image(self.realmap, 'realmap', 100)
        
    def turn(self, info):
        realmap, map = self.analyseMap(info)
        me = info['snakes'][self.seq]['body']
        ret = self.possible(me, realmap, info)
        #print "my length %s"%len(me)
        
        #debug info
        if self.debug:
            #self.info2txt(info,'info_%s'%info['round'])
            pass
        #print "ret %s" % ret
        
        path = self.analyseBean(info, realmap)
        
        if len(path) > 0:
            bestpath, bestv = None, (0,1000)
            for pk,pv in path.items():
                if bestv[0]<pv[0] and (bestv[0]-bestv[1])<=(pv[0]-pv[1]):
                    bestpath = pk
            dir = self.direction[self.sub(bestpath, me[0])]
            if dir in ret:
                return dir
        
        for r in ret[:]:
            pt = self.move(me[0], self.offset[r])
            if self.mapget(realmap, pt) == self.typec['opbeanw']:
                ret.remove(r)
            
        """
        find best ranked direction
        """
        #print "calculate rank: %s"%ret
        bestr, bestv = random.randint(0,3), 100000
        
        for r in ret:
            tpt = self.move(me[0], self.offset[r])
            v = 0
            for x in range(self.size[0]):
                for y in range(self.size[1]):
                    if x!=me[0][0] and y!=me[0][1]:
                        dist = self.mandist((x,y), tpt)
                        v += map[x][y] / (dist * dist)
            if v < bestv:
                bestr, bestv = r, v
            #print "dir %s - value %s"%(r,v)
        #print "select %s"%bestr
        return bestr
    
    def possible(self, me, realmap, info):        
        dir = [0, 1, 2, 3]        
        dir.remove(self.direction[self.sub(me[1], me[0])])
        
        for d in dir[:]:
            pt = self.move(me[0], self.offset[d])
            if self.mapget(realmap, pt) != self.EMPTY and \
                self.mapget(realmap, pt) != self.typec['beanw'] and \
                not (len(me)>7 and self.mapget(realmap, pt) == self.typec['opbeanw']):
                dir.remove(d)
                continue
            if len(dir)>0:
                for snake in info['snakes']:
                    body = snake['body']
                    if body == me: continue
                    if self.mandist(body[0], pt) == 1:
                        dir.remove(d)
                        break        
        return dir
        
    """
    analyse map
    """
    def analyseMap(self, info):
        map = self.mapcopy(self.analmap)
        realmap = self.mapcopy(self.realmap)
        
        for pt in info[self.typec['bean']]:
            self.radia(map, pt, -60, 2)
            self.mapset(realmap, pt, self.typec['beanw'])
        
        for pt in info[self.typec['opbean']]:
            self.radia(map, pt, 40, 2)
            self.mapset(realmap, pt, self.typec['opbeanw'])
            
        for id in range(len(info['snakes'])):
            if id in self.dead: continue
            snake = info['snakes'][id]
            if id != self.seq:
                if snake['alive']:
                    danger = 80
                    for pt in snake['body']:
                        self.radia(map, pt, danger, 2)
                        self.mapset(realmap, pt, self.SNAKE + id)
                        danger = max(0, danger-2)
                else:
                    self.dead.append(id)
                    self.addwall(snake['body'], self.realmap, self.analmap)
                    self.addwall(snake['body'], realmap, map)                    
            else:
                danger = 60
                for pt in snake['body']:
                    self.radia(map, pt, danger, 2)
                    self.mapset(realmap, pt, self.SNAKE + id)
                    danger = max(0, danger-2)
        
        if self.debug:
            self.map2image(realmap, 'realmap_%s'%info['round'], 100)
            self.map2image(map, 'analmap_%s'%info['round'], 300)
            pass
        return (realmap, map)
        
    """
    analyse beans
    """
    def analyseBean(self, info, realmap):        
        bfsmap, eat = [], []
        for snake in info['snakes']:
            if snake['type'] == self.type:
                bmap = self.bfs(realmap, snake['body'][0])
                bfsmap.append(bmap)
                toeat, mindist = [], self.size[0]*self.size[1]
                for bean in info[self.typec['bean']]:
                    v = self.mapget(bmap, bean)
                    if v<mindist:
                        toeat = [tuple(bean)]
                        mindist = v
                    elif v == mindist:
                        toeat.append(tuple(bean))
                eat.append((toeat,mindist))
            else:
                bfsmap.append(None)
                eat.append(([],0))
        
        opbfsmap = self.bfs(realmap, info['snakes'][self.seq]['body'][0], True)
        
        #print "eat:%s"%eat
        mine = {}
        for bean in info[self.typec['bean']]:
            mine[tuple(bean)] = self.mapget(bfsmap[self.seq], bean)
        
        #print 'before remove: %s'%mine
        for bs,v in eat: 
            for b in bs:
                if b in mine.keys() and mine[b] > v: 
                    opv = self.mapget(opbfsmap, b)
                    if opv < v and len(info['snakes'][self.seq]['body'])>10:
                        # even it cost a op bean, just go through
                        mine[b] = opv
                    else:
                        del mine[b]        
        #print 'after remove: %s'%mine
        
        for bean,dist in mine.items():
            bmap = self.bfs(realmap, bean)
            weight, blen = 0.0, len(info[self.typec['bean']])
            for obean in info[self.typec['bean']]:
                if tuple(obean) != bean:
                    weight += self.mapget(bmap, obean) * 1.0 / blen
                    blen -= 1
            mine[bean] = (dist, weight)
        
        #print 'mine %s'%mine
        
        cpath, weight = {}, 10000
        for bean,wt in mine.items():
            bwt = wt[0] #* 1.5 + wt[1]*0.5
            if bwt < weight:
                if self.mapget(bfsmap[self.seq], bean) == wt[0]:
                    cpath = self.path(bfsmap[self.seq], realmap, bean)
                else:
                    cpath = self.path(opbfsmap, realmap, bean)
                weight = bwt
        
        #print cpath
        return cpath
    
    """ 
    utilities 
    """
    def initmap(self, fill):
        return [[fill] * self.size[1] \
            for i in range(self.size[0])]
    
    def addwall(self, walls, realmap, map):
        for pt in walls:
            self.mapset(realmap, pt, self.WALL)
            self.radia(map, pt, 60, 4)
        moreWall = True
        while moreWall:
            moreWall = False
            for x in range(self.size[0]):
                for y in range(self.size[1]):
                    walls = 0
                    for oft in self.offset:
                        pt = self.move((x,y), oft)
                        if self.mapget(realmap, pt) == self.WALL:
                            walls += 1
                    if walls > 2 and self.mapget(realmap, (x,y)) != self.WALL:
                        self.mapset(realmap, (x,y), self.WALL)
                        moreWall = True
            
    
    def radia(self, map, pt, danger, factor):
        self.mapset(map, pt, danger)
        danger /= factor
        n = 1
        while abs(danger) > 1:
            for i in range(-n, n):
                self.mapadd(map, self.move(pt, (i, -n)), danger)
                self.mapadd(map, self.move(pt, (i, n)), danger)
                self.mapadd(map, self.move(pt, (-n, i)), danger)
                self.mapadd(map, self.move(pt, (n, i)), danger)
                
            danger /= factor
            n += 1
            
    def move(self, pt, oft, scale=1):
        return (((pt[0] + oft[0]*scale + self.size[0]) % self.size[0]) \
            , (pt[1] + oft[1]*scale + self.size[1]) % self.size[1])
        
    def mapget(self, map, pt):
        return map[pt[0]][pt[1]]
        
    def mapset(self, map, pt, v):
        map[pt[0]][pt[1]] = v
    
    def mapadd(self, map, pt, add):
        map[pt[0]][pt[1]] += add
    
    def mapcopy(self, map):
        ret = []
        for a in map:
            row = []
            for i in a:
                row.append(i)
            ret.append(row)
        return ret
        
    def mincord(self, pt1, pt2, cord):
        min1 = pt1[cord] - pt2[cord]
        min2 = pt1[cord] + self.size[cord] - pt2[cord]
        min3 = pt1[cord] - self.size[cord] - pt2[cord]
        if abs(min1) < abs(min2) and abs(min1) < abs(min3):
            min = min1
        elif abs(min2) < abs(min3):
            min = min2
        else:
            min = min3
        return min
    
    def sub(self, pt1, pt2):
        return (self.mincord(pt1,pt2,0), self.mincord(pt1,pt2,1))
    
    def mandist(self, pt1, pt2):
        return (abs(pt1[0]-pt2[0])+abs(pt1[1]-pt2[1]))
    
    def bfs(self, realmap, pt, op=False):        
        vmap = self.initmap(self.size[0] + self.size[1])      
        queue = [pt]
        self.mapset(vmap, pt, 0)
        while len(queue)>0:
            tp = queue.pop(0)
            tv = self.mapget(vmap, tp)
            for oft in self.offset:
                np = self.move(tp, oft)
                type = self.mapget(realmap, np)
                if (type == self.EMPTY or \
                    type == self.typec['beanw'] or \
                    (op and type == self.typec['opbeanw'])) and \
                    self.mapget(vmap, np) > tv+1:
                    self.mapset(vmap, np, tv+1)
                    queue.append(np)
        return vmap
    
    def path(self, map, realmap, pt):
        step = self.mapget(map, pt) - 1
        pt = tuple(pt)
        # path sturct: (points, eat my bean, eat op bean)
        path = {pt:(1,0)}
        while step>0:
            npath = {}
            for p,b in path.items():
                for oft in self.offset:
                    next = self.move(p, oft)
                    if self.mapget(map, next) == step:
                        tmy, top = b[0], b[1]
                        if self.mapget(realmap, next) == self.typec['beanw']:
                            tmy += 1
                        elif self.mapget(realmap, next) == self.typec['opbeanw']:
                            top += 1
                        if next not in npath.keys() or \
                            (npath[next][0] - npath[next][1] < tmy -top or\
                            npath[next][0] < tmy or npath[next][1] > top):
                            npath[next] = (tmy, top)
            path = npath
            step -= 1
        return path
    
    def pt2color(self, map, pt, max):
        v = self.mapget(map, pt)
        c = 100 - min(v,max) * 100 / max
        h = 3.6 * c
        
        return ImageColor.getcolor('hsl('+str(int(h))+','+str(c)+'%,'+str(c)+'%)', 'RGB')
    
    def map2image(self, map, imgname, max):
        data = []
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                data.append(self.pt2color(map, (x,y), max))
        
        img = Image.new('RGB', (50,25))
        img.putdata(data)
        img.save('%s/%s.png'%(self.TMP,imgname))
        
    def info2txt(self, info, infoname):
        with open('%s/%s.txt'%(self.TMP, infoname), 'w') as f:
            f.write(str(info))