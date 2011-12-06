#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: zmq_pygame_show
"""
from lib import *
from pygame_show import Shower

import zmq
context = zmq.Context()

usage = """
python zmq_pygame_show.py [room number]
"""

def show(room):
    """
    用来显示现在游戏状况的client
    """
    # 用来接受info更新
    suber = context.socket(zmq.SUB)
    suber.connect('ipc:///tmp/game_puber.ipc')
    suber.setsockopt(zmq.SUBSCRIBE, "room:%d " % room)
    # 用来与服务器交互
    oper = context.socket(zmq.REQ)
    oper.connect('ipc:///tmp/game_oper.ipc')
    # 获取map
    def get_map():
        req = dict(op='map', room=room)
        oper.send(json.dumps(req))
        return json.loads(oper.recv())
    m = get_map()

    clock = Clock(30)
    shower = Shower(m)
    info = None
    
    while True:
        clock.tick()
        # 等待地图更新...
        try:
            info = suber.recv(zmq.NOBLOCK)
            info = info[info.index(' ') : ]
            info = json.loads(info)
            # 如果游戏结束了, 获取map
            if info['status'] == 'waitforplayer':
                shower.set_map(get_map())
            
        except zmq.ZMQError as e:
            pass

        if info:
            shower.flip(info)


if __name__=="__main__":
    try:
        room = int(sys.argv[1])
    except:
        print usage
    show(room)
