#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: zmq_replayer
"""
from lib import *

import zmq
context = zmq.Context()


def replayer(filename="game.log", loop=False):
    """
    用来回放log, 默认room0
    """
    if loop: loop_count=0
    # 读取file
    datas = []
    with open(filename) as f:
        for line in f.readlines():
            p = line.find(': ')
            type = line[:p]
            data = line[p+len(': '):]
            data = json.loads(data)
            datas.append((type, data))

    # 用来发布信息更新
    puber = context.socket(zmq.PUB)
    puber.bind('ipc:///tmp/game_puber.ipc')

    # 用来处理
    oper = context.socket(zmq.REP)
    oper.bind('ipc:///tmp/game_oper.ipc')

    clock = Clock(2)
    i = 0
    map = None
    info = None
    
    while True:
        # 处理op
        while True:
            try:
                rc = json.loads(oper.recv(zmq.NOBLOCK))
                if rc['op'] not in ('map', 'info'):
                    result = 'this is replay server, only accept map and info'
                if rc['op'] == 'map':
                    result = map
                else:
                    result = info
                oper.send(json.dumps(result))
                logging.debug('process op %s ', rc['op'])
            except zmq.ZMQError:
                break
            
        #定时更新
        if not clock.tick(block=False):
            continue

        # get data
        type, data = datas[i]
        i += 1
        if i == len(datas): break
        
        if type == 'map':
            map = data
            continue
        else:
            info = data

        logging.debug("stepping:" + info['status'])
        # 发送更新信息
        puber.send("room:0 " + json.dumps(info))
        
        time.sleep(0.001)

usage = """\
    zmq_replayer.py [filename]
"""

if __name__=="__main__":
    if len(sys.argv) <1: print usage
    replayer(filename)
