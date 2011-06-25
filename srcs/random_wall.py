#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: generate random wall
"""
import random
from game import *
        
class RandomWallGen(WallGen):
    offset = [[-1,0],[1,0],[0,-1],[0,1]]	# 4 directions
    minDensity, maxDensity = 0.05, 0.07		# in [0,1]
    discrete, straight = 0.15, 0.5			# in [0,1]
    
    
    def can(self, ctx):
        """
        in simple mode, only generate wall before game start
        """
        return ctx.round == 0 and ctx.status == 'initial'
    def gen(self, ctx):
        """
        generate random map
        """
        wall = self.genWall(ctx)
        #wall = [[12,13], [12,14], [12,15], [13,15], [14,15], [15,14], [15,13], [14,13], [13,13]]
        #wall = [[7,5],[6,6],[8,6],[5,7],[9,7],[6,8],[8,8],[7,9]]
        #wall = [[7,8],[8,8],[10,8],[5,9],[6,9],[8,9],[9,9],[10,9],[5,10],[6,10],[7,10],[9,10],[6,11],[8,11],[9,11]]
        return self.breakWall(ctx, wall)
        
        
    def genWall(self, ctx):
        """
        generate map with random algorithm
        """
        num = ctx.w * ctx.h * random.uniform(self.minDensity, self.maxDensity)
        walls = []
        
        # check point in bound or not
        def bound(pt):
            return pt[0]>=0 and pt[0]<ctx.w and pt[1]>=0 and pt[1]<ctx.h
        
        # pick a point from neighbours
        self.idxes = range(4)
        random.shuffle(self.idxes)
        def next(pt):
            if random.random() > self.straight:
                random.shuffle(self.idxes)
            for i in self.idxes:
                dt = self.offset[i]
                dp = [pt[0]+dt[0], pt[1]+dt[1]]
                if bound(dp):
                    for wp in walls:
                        if dp == wp: dp = None; break
                    if dp is not None:
                        return dp
            return None
        
        # generate num points to construct the walls
        while num>0:
            # start point of a wall
            pt = [random.randint(0, ctx.w-1), random.randint(0, ctx.h-1)]
            if pt in walls: continue
            walls += [pt]
            num -= 1
            
            # continue grow the wall
            while random.random()>self.discrete and num>0:
                np = next(pt)
                if np == None: break
                walls += [np]
                pt = np
                num -= 1
        
        return walls
    
    def breakWall(self, ctx, walls):
    	"""
    	break the closed area:
    	1. calculate union set of the area
    	2. break the wall between different area
    	"""
    	set = [ [j*ctx.h+i for i in range(ctx.h)] for j in range(ctx.w)]

        for pt in walls:
            set[pt[0]][pt[1]] = -1

        move = lambda pt,dt=(0,0): [(pt[0]+dt[0]+ctx.w)%ctx.w, (pt[1]+dt[1]+ctx.h)%ctx.h]
        inset = lambda pt: set[pt[0]][pt[1]]
        setv = lambda pt,v: set[pt[0]].__setitem__(pt[1], v)
        setvp = lambda pt,vp: set[pt[0]].__setitem__(pt[1], set[vp[0]][vp[1]])
        idxtopt = lambda idx: [idx/ctx.h, idx%ctx.h]
        parent = lambda pt: idxtopt(inset(pt))
        
        def root(pt):
            if inset(pt) < 0: return -1
            t = pt
            while parent(t) != t:
                t = parent(t)
            tp = pt
            while parent(tp) != t:
                pt, tp = tp, parent(tp)
                setvp(pt, t)
            return inset(t)

        def union(pt1, pt2):
            rt1, rt2 = root(pt1), root(pt2)
            if rt1 < rt2:
                setv(idxtopt(rt2), rt1)
            elif rt2 < rt1:
                setv(idxtopt(rt1), rt2)

        # union the connected points
        def connect(pt):
            if root(pt) < 0 : return

            pt1 = move(pt, (-1,0))
            pt2 = move(pt, (0,-1))
            if root(pt1)>=0:
                union(pt, pt1)
            if root(pt2)>=0:
                union(pt, pt2)

        # build connection relationship
        for y in range(ctx.h):
            for x in range(ctx.w):
                connect((x,y))

        rtcnt = {}
        for y in range(ctx.h):
            for x in range(ctx.w):
                rt = root((x,y))
                if rt < 0 : continue
                if rt in rtcnt.keys():
                    rtcnt[rt] += 1
                else:
                    rtcnt[rt] = 1

        maxrt, maxrtcnt = 0, 0
        for k,v in rtcnt.items():
            if v > maxrtcnt: maxrt, maxrtcnt = k, v

        # break the closed area by removing blocking wall
        while len(rtcnt)>1:
            for pt in walls:
                for dt in self.offset:
                    tp = move(pt, dt)
                    rt = root(tp)
                    if rt>=0 and rt!=maxrt:
                        walls.remove(pt)
                        setv(pt, rt)
                        break
                if root(pt)>=0:
                    for dt in self.offset:
                        tp = move(pt, dt)
                        root1, root2 = root(pt), root(tp)
                        if root1>=0 and root2>=0 and root1!=root2:
                            union(tp, pt)
                            del rtcnt[max(root1,root2)]
        return walls
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
