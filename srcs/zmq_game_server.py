#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: server
"""
from lib import *
import zmq, json, random

import ai_simple, game_controller
from snake_game import *

context = zmq.Context()

ROOMS = 5

class Server():
    """
    游戏的服务器逻辑
    服务器提供2个队列:
    - game_puber队列(PUB), 当地图更新的时候, 发送info信息
    - game_oper队列(REP), 可以进行add/turn/map命令
    """
    def on_logic(self, g, ok):
        """判断定期更新的时间是否到了"""
        min_waits = 0.2
        max_waits = self.max_waits
        if not hasattr(g, 'pre'):
            g.pre = time.time()

        # 时间段不能小于min_waits, 不能大于max_waits
        now = time.time()
        if (now > g.pre + max_waits
            or (ok and now > g.pre + min_waits)
            ):
            g.pre = now
            return True
        
    def run(self, max_waits=10.0, enable_no_resp_die=True):
        self.max_waits = max_waits
        self.games = [Game(enable_no_resp_die=enable_no_resp_die)
                      for i in range(ROOMS)]
        self.controller = game_controller.RoomController(self.games)
        
        # 用来发布信息更新
        puber = context.socket(zmq.PUB)
        puber.bind('ipc:///tmp/game_puber.ipc')

        # 用来处理
        oper = context.socket(zmq.REP)
        oper.bind('ipc:///tmp/game_oper.ipc')

        while True:
            time.sleep(0.001)
            
            # 处理op
            while True:
                try:
                    rc = oper.recv(zmq.NOBLOCK)
                # 处理完所有命令就跳出命令处理逻辑
                except zmq.ZMQError:
                    break

                try:
                    rc = json.loads(rc)
                    result = self.controller.op(rc)
                    result['op'] = rc['op']
                    # logging.debug('process op %s ', rc)
                # 为了防止错误命令搞挂服务器, 加上错误处理
                except Exception as e:
                    error_msg = str(e)
                    result = dict(status=error_msg)
                    logging.debug(error_msg)
                    
                oper.send(json.dumps(result))

            # 处理所有room的游戏id
            for i, g in enumerate(self.games):

                if g.status == RUNNING:
                    # 当游戏进行时, 需要等待所有活着的玩家操作完毕
                    ok = g.alloped()
                else:
                    # 其他状态的话, 最小时间的方式定时更新                    
                    ok = True
                    
                if not self.on_logic(g, ok):
                    continue
    
                # 游戏处理
                g.step()
                # logging.debug("room %d stepping: %s" % (i, g.status))
                # 发送更新信息
                info = self.controller.op(
                    dict(room=i, op='info'))
                info['op'] = 'info'
                puber.send("room:%d "%i + json.dumps(info))

usage = """\
    $ zmq_game_server.py [type]
    type == server:
        default game server.
    type == 4web:
        server for snakechallenge.org, when game over, server start new round.
    type == 4webai:
        because it is slow on internet, set wait time to 10.0 seconds        
"""

def main():
    import sys
    if len(sys.argv) < 2: print usage
    cmd = sys.argv[1]
    if cmd == 'server':
        s = Server()
        s.run()
    elif cmd == '4web':
        s = Server()
        s.run(max_waits=1.0, enable_no_resp_die=False)
    elif cmd == '4webai':
        s = Server()
        s.run(max_waits=10.0)
    else:
        print usage
        
if __name__=="__main__":
    main()
