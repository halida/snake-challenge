from utils import AIBase, startGame, dirVec
from copy import deepcopy
# weight:
kDanger = 100 # void danger
kArea = -0.3

def rd(w, x):
    return min(x, w - x)

class SnackAI(AIBase):
    def __init__(self):
        AIBase.__init__(self, "kitty-snake")
    
    def newRound(self, roundId):
        me = self.snakes[self.idx]
        if not me['alive']:
            print "new round: %d, dying" % roundId
            return
        print "new round: %d" % roundId
        body = me['body']
        x, y = body[0]
        tail = body[-1]
        myLen = len(body)
        m = self.buildMap(myLen < 5) # void gem when my len < 5
        fm = self.buildFakeMap(m)
        otherLen = 0
        for i in range(len(self.snakes)):
            if i != self.idx and self.snakes[i]['alive']:
                otherLen = max(otherLen, len(self.snakes[i]['body']))
        dir = me['direction']
        ntegg = 1000000
        valueK = 1
        if myLen - otherLen > 10:
            valueK = 0
        elif myLen > otherLen:
            valueK = (10 + otherLen - myLen) / 10
        for d, nx, ny in self.graph[me['direction']][x][y]:
            if m[nx][ny] != 0:
                print m[nx][ny], (x, y), 
                continue
            toegg, danger = self.calcValue(m, nx, ny, d, tail)
            value1 = toegg * valueK + danger * kDanger + self.sumArea(m, (nx, ny)) * kArea
            toegg, danger = self.calcValue(fm, nx, ny, d, tail)
            value2 = toegg * valueK + danger * kDanger + self.sumArea(m, (nx, ny)) * kArea
            finalValue = value1 + value2 * 0.5
            if finalValue < ntegg:
                ntegg = finalValue
                dir = d
        print (x, y), "ntegg=", ntegg
        self.turn(dir)

    def move(self, x, y, d):
        return [(x + dirVec[d][0] + self.w) % self.w, (y + dirVec[d][1] + self.h) % self.h]

    def dist(self, a, b):
        return rd(self.w, abs(a[0] - b[0])) + rd(self.h, abs(a[1] - b[1]))

    def calcValue(self, map, mx, my, d, t):
        g = self.graph
        value = 100
        x, y = mx, my
        if [x, y] in self.eggs:
            value = 0
        danger = 2
        v = ([], [], [], [])
        for i in range(4):
            for j in range(self.w):
                v[i].append([False] * self.h)

        # print d, x, y
        v[d][x][y] = True
        q = [(d, x, y, 1)]
        f = 0
        tailFlag = 0
        while f < len(q):
            d, x, y, st = q[f]
            # print f, d, x, y, st
            # print (x, y), st
            f += 1
            for nd, nx, ny in g[d][x][y]:
                # print "inloop:", nd, (nx, ny), map[nx][ny], v[nd][nx][ny]
                if not v[nd][nx][ny]:
                    if map[nx][ny] < st and map[nx][ny] >= 0:
                        v[nd][nx][ny] = True
                        q.append((nd, nx, ny, st+1))
                        if (nx, ny) == tuple(t):
                            tailFlag = 1
                        elif [nx, ny] in self.eggs:
                            value = min(value, st)
        danger -= tailFlag
        nearKill = 0
        for i in range(len(self.snakes)):
            if i != self.idx and self.snakes[i]['alive']:
                if self.snakes[i]['sprint'] == 0:
                    if self.dist((x, y), self.snakes[i]['body'][0]) <= 1:
                        nearKill = 1
                    else:
                        ex, ey = self.snakes[i]['body'][0]
                        for i in range(3):
                            ex, ey = self.move(ex, ey, self.snakes[i]['direction'])
                        if (ex, ey) == (x, y):
                            nearKill = 1
                elif self.snakes[i]['sprint'] > 0 and self.dist((x, y), self.snakes[i]['body'][0]) <= 3:
                    nearKill = 1
        danger += nearKill

        for i in range(len(self.snakes)):
            if i != self.idx:
                map[mx][my] = -1
                ret = self.checkAttack(map, self.snakes[i])
                map[mx][my] = 0
                if ret:
                    value = -1
	return value, danger

    def sumArea(self, map, st):
        v = []
        for i in range(self.w):
            v.append([False] * self.h)
        x, y = st
        v[x][y] = True
        q = [(x, y)]
        f = 0
        while f < len(q):
            x, y = q[f]
            f += 1
            for d in range(4):
                nx, ny = self.move(x, y, d)
                if not v[nx][ny] and map[nx][ny] == 0:
                    v[nx][ny] = True
                    q.append((nx, ny))
        #print "area:", f
        return f

    def checkAttack(self, map, snake):
        if not snake['alive']:
            return False
        return self.sumArea(map, snake['body'][0]) <= len(snake['body'])
        
    def buildMap(self, noGem):
        m = []
        for i in range(self.w):
            m.append([0] * self.h)
        for x, y in self.walls:
            m[x][y] = -1
        for snake in self.snakes:
            if snake['alive']:
                count = len(snake['body'])
                for x, y in snake['body']:
                    m[x][y] = count
                    count -= 1
            else:
                for x, y in snake['body']:
                    m[x][y] = -1
        if noGem:
            for x, y in self.gems:
                m[x][y] = -1
        # for i in m:
        #     print i
	return m

    def buildFakeMap(self, map):
        fakeMap = deepcopy(map)
        for i in range(len(self.snakes)):
            if i != self.idx and self.snakes[i]['alive'] and self.snakes[i]['sprint'] >= 0:
                hx, hy = self.snakes[i]['body'][0]
                val = len(self.snakes[i]['body']) + 1
                for d in self.getDirs(self.snakes[i]['direction']):
                    if fakeMap[hx][hy] >= 0 and fakeMap[hx][hy] <= val:
                        fakeMap[hx][hy] = val
        return fakeMap

    def buildGraph(self):
        # Build The Basic Graph for BFS
        # first: Dir 0 ~ 3
        # then x, y
        g = ([],[],[],[]) 
        for i in range(4):
            print "build-direction:", i
            for x in range(self.w):
                line = []
                for y in range(self.h):
                    cell = []
                    for d in self.getDirs(i):
                        if [x, y] in self.walls:
                            break
                        nx, ny = self.move(x, y, d)
                        for pi in range(len(self.portals)):
                            if (nx, ny) == tuple(self.portals[pi]):
                                print "detect portal: ", pi, (nx, ny)
                                if pi % 2 == 1: 
                                    di = pi - 1
                                else:
                                    di = pi + 1 
                                # set sx, sy to out portal addr
                                nx, ny = self.portals[di]
                                break

                        if [nx, ny] not in self.walls:
                            cell.append((d, nx, ny))
                        
                    line.append(cell)
                g[i].append(line)
        return g
                    
    def onUpdateMap(self):
        print "Building Graph..."
        self.graph = self.buildGraph()
        print "Building Graph finish."



host = 'localhost'
# host = 'game.snakechallenge.org'
startGame("ws://%s:9999/info" % host, 0, SnackAI())
