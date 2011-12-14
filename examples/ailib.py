#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: ailib
提供ai辅助的一些工具
"""
import sys, os
import urllib, httplib 
import time, logging, json, random, uuid, datetime
from datetime import date

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# 方向对应修改的坐标
DIRECT = (
    (-1, 0), (0, -1), (1, 0), (0, 1)
    )

class BaseAI():
    def setmap(self, map):
        pass
    def step(self, info):
        pass

def get_dirs(body):
    """
    输入蛇的body, 计算出对应有效的direction
    >>> get_dirs([[1, 2], [1, 3]])
    [(-1, 0), (0, -1), (1, 0)]
    """
    fx = body[0][0] - body[1][0]
    fy = body[0][1] - body[1][1]
    if fx > 1: fx = -1
    if fx < -1: fx = 1
    if fy > 1: fy = -1
    if fy < -1: fy = 1
    backward = -fx, -fy

    dirs = list(DIRECT)
    try:
        dirs.remove(backward)
    except:
        # in portal or some case, dirs is wrong
        pass
    return dirs

def near(a, b, size):
    ax, ay = a
    bx, by = b
    sw, sh = size
    nearx = (abs(ax-bx) <= 1) or (ax==0 and bx==sw-1) or (ax==sw-1 and bx==0)
    neary = (abs(ay-by) <= 1) or (ay==0 and by==sh-1) or (ay==sh-1 and by==0)
    if nearx and neary:
        return True

def get_distance(a, b, size):
    ax, ay = a
    bx, by = b
    sw, sh = size

    if ax == bx:
        disx, dirx = 0, 0
    else:
        dxs = [[(bx-ax+sw)%sw, -1],
               [(ax-bx+sw)%sw, +1]]
        disx, dirx = min(dxs)

    if ay == by:
        disy, diry = 0, 0
    else:
        dys = [[(by-ay+sh)%sh, -1],
               [(ay-by+sh)%sh, +1]]
        disy, diry = min(dys)
    
    return (disx, disy), (dirx, diry)

class WebController():
    """
    提供给ai操作的web接口
    """
    def __init__(self, room):
        self.addr = 'game.snakechallenge.org:9999'
        self.room = room
        self.conn = httplib.HTTPConnection(self.addr)

    def cmd(self, cmd, data={}):
        """
        发送命令给服务器
        """
        data['op'] = cmd
        data['room'] = self.room
        # logging.debug('post: %s : %s', cmd, data)
        self.conn.request("POST", '/cmd',
                          urllib.urlencode(data),
                          {'Content-Type': 'application/x-www-form-urlencoded'})
        result = self.conn.getresponse().read()
        return json.loads(result)

    def add(self, name, type):
        self.me = self.cmd("add",
                           dict(name = name,
                                type = type))
        return self.me
    
    def map(self):
        return self.cmd("map")

    def info(self):
        return self.cmd("info")

    def turn(self, dir):
        return self.cmd("turn",
                        dict(id = self.me["id"],
                             round = -1,
                             direction = dir))
    def sub_info(self):
        time.sleep(0.3)
        return self.info()


class ZeroController():
    """
    提供给ai操作的zeromq接口
    """
    def __init__(self, room):
        import zmq
        self.zmq = zmq
        context = zmq.Context()
        self.room = room
        # 用来接受info更新
        self.suber = context.socket(zmq.SUB)
        self.suber.connect('ipc:///tmp/game_puber.ipc')
        self.suber.setsockopt(zmq.SUBSCRIBE, 'room:%d '%room)
        # 用来与服务器交互
        self.oper = context.socket(zmq.REQ)
        self.oper.connect('ipc:///tmp/game_oper.ipc')
        # poller
        self.poller = zmq.Poller()
        self.poller.register(self.suber, zmq.POLLIN)

    def op(self, op, kw=None):
        if not kw: kw = dict()
        kw['op'] = op
        kw['room'] = self.room
        self.oper.send(json.dumps(kw))
        return json.loads(self.oper.recv())

    def map(self):
        return self.op('map')

    def add(self, name, type):
        self.me = self.op(
            'add', dict(name=name,
                        type=type))
        return self.me

    def info(self):
        return self.op('info')

    def sub_info(self):
        socks = dict(self.poller.poll(timeout=5000))
        if self.suber in socks and socks[self.suber] == self.zmq.POLLIN:
            info = self.suber.recv()
            info = info[info.index(' '):]
            info = json.loads(info)
        else:
            info = self.info()
        return info
    
    def turn(self, d, round=-1):
        return self.op(
            'turn', dict(id=self.me['id'],
                         direction=d,
                         round=round))


def run_ai(ai, controller):
    """
    执行ai
    """
    c = controller
    # 初始化状态
    NEED_ADDING, RUNNING = range(2)
    ai.status = NEED_ADDING
    
    while True:
        time.sleep(0.01)
        # 先获取场上的情况
        if False:#ai.status == NEED_ADDING:
            info = c.info()
        else:
            info = c.sub_info()

        # found me
        names = [s['name'] for s in info['snakes']]
        if ai.name in names:
            me = info['snakes'][names.index(ai.name)]
        else:
            me = None

        # need add to game
        if ai.status == NEED_ADDING:
            # if already added, not add again
            if me: continue
            
            # 游戏结束的时候就不上场了.
            if info['status'] == 'finished':
                logging.debug('finished, waiting for adding..')
                time.sleep(1)
                continue

            # add ai
            result = c.add(ai.name, ai.type)
            if not result.has_key('seq'): # cannot enter?
                continue
            ai.seq = result['seq']
            ai.id = result['id']
            ai.status = RUNNING
            # 告诉ai地图
            m = c.map()
            ai.setmap(m)
            logging.debug("add ai: %d" % ai.seq)
            continue

        if info['status'] == 'finished':
            # 游戏结束的话, 或者发现没有蛇的信息, ai复位..
            ai.status = NEED_ADDING
            # print "not me"
            continue
        if not me: continue

        # 如果自己死掉了, 那就不发出操作
        if not me['alive']:
            logging.debug(ai.name+' is dead.')
            ai.status = NEED_ADDING            
            # print "not alive"
            continue

        # 发出操作
        try:
            d = ai.step(info)
        except Exception as e:
            raise
            logging.debug(str(e))
            ai.status == NEED_ADDING
            continue
        result = c.turn(d)

        # 操作失败显示下
        if result['status'] != 'ok':
            logging.debug(result['status'])
        # logging.debug("turn: %d in round: %d", d, info['round'])

def cmd_run(AI):
    usage = """\
    $ %s [connect type] [room number] [ai number]
    connect type is in [web, zero]
        web means use Restful http API,
        zero means use zeromq.
        ai number means how much ai you are running
        """%sys.argv

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

    if len(sys.argv) > 3:
        def run():
            run_ai(AI(), C(room))
        import multiprocessing
        ps = [multiprocessing.Process(target=run, args=())
              for i in range(int(sys.argv[3]))]
        for p in ps: p.start()
        for p in ps: p.join()
    else:
        run_ai(AI(), C(room))

def main():
    import doctest
    doctest.testmod()

if __name__=="__main__":
    main()

