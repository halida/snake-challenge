#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: ailib
提供ai辅助的一些工具
"""
from lib import *
import urllib, httplib 

from snake_game import Game, FINISHED, DIRECT
from game_controller import Controller

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
    dirs.remove(backward)
    return dirs


class WebController():
    """
    提供给ai操作的web接口
    """
    def __init__(self, room):
        self.addr = 'snakechallenge.org'#'127.0.0.1:8080'
        self.room = room
        self.conn = httplib.HTTPConnection(self.addr)

    def get(self, url):
        self.conn.request("GET", '/room/%d/%s' % (self.room, url))
        response = self.conn.getresponse()
        result = response.read()
        return json.loads(result)

    def post(self, url, kw):
        self.conn.request(
            "POST",
            '/room/%d/%s' % (self.room, url),
            urllib.urlencode(kw))
        response = self.conn.getresponse()
        result = response.read()
        return json.loads(result)

    def map(self):
        return self.get('map')

    def add(self, name, type):
        result = self.post(
            'add', dict(name=name,
                        type=type))
        # todo 唉. web api还是要改改?
        result = result[0]
        return result

    def info(self):
        return self.get('info')
    
    def turn(self, id, d, round=-1):
        result = self.post(
            'turn', dict(id=id,
                         direction=d,
                         round=round))
        # todo 唉. web api还是要改改?
        result = result[0]
        return result


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

    def op(self, op, kw=None):
        if not kw: kw = dict()
        kw['op'] = op
        kw['room'] = self.room
        self.oper.send(json.dumps(kw))
        return json.loads(self.oper.recv())

    def map(self):
        return self.op('map')

    def add(self, name, type):
        return self.op(
            'add', dict(name=name,
                        type=type))

    def info(self):
        info = self.suber.recv()
        # try:
        #     while True:
        #         info = self.suber.recv(self.zmq.NOBLOCK)
        # except self.zmq.ZMQError:
        #     pass
            
        info = info[info.index(' '):]
        return json.loads(info)
    
    def turn(self, id, d, round=-1):
        return self.op(
            'turn', dict(id=id,
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
        # 先获取场上的情况
        info = c.info()

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

        if info['status'] == 'finished' or not me:
            # 游戏结束的话, 或者发现没有蛇的信息, ai复位..
            ai.status = NEED_ADDING
            continue

        # 如果自己死掉了, 那就不发出操作
        if not me['alive']:
            logging.debug(ai.name+' is dead.')
            ai.status = NEED_ADDING            
            continue

        # 发出操作
        d = ai.step(info)
        result = c.turn(ai.id, d)

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

