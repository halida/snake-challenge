#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: game_controller
游戏控制器.. 提供api级别的接口, 方便服务器调用game

"""
from snake_game import *

class RoomController():
    def __init__(self, games):
        self.games = games
        self.controllers = [Controller(g)
                            for g in self.games]
    def op(self, data):
        """
        分配room
        """
        # 检查room
        if not data.has_key('room'):
            return dict(status = "data has no room param.")
        
        try:
            room = int(data['room'])
        except Exception as e:
            return dict(status="room data (%s) error: %s" % (data['room'], str(e)))
        
        if not 0 <= room < len(self.games):
            return dict(status='room number error: %d'%room)
        # 分配处理
        return self.controllers[room].op(data)

class Controller():
    def __init__(self, game):
        self.game = game

    def op(self, data):
        """
        统一的op接口
        """
        op = data['op']
        if op == 'add':
            return self.game.add_snake(type=data['type'], name=data['name'])
        
        elif op in ('turn', 'sprint'):
            if not data.has_key(round): data['round'] = -1
            return dict(status=self.game.set_snake_op(data['id'], int(data['round']), data))
        
        elif op == 'map':
            return self.game.get_map()

        elif op == 'setmap':
            return dict(status=self.game.user_set_map(data['data']))
        
        elif op == 'info':
            return self.game.get_info()
        
        elif op == 'history':
            return self.history()
        
        elif op == 'scores':
            return self.game.scores()
        
        else:
            return dict(status='op error: %s' % op)

def test():
    """
    # 初始化
    >>> game = Game()
    >>> c = Controller(game)

    # 添加新的蛇
    >>> result = c.add(name='foo',type='python')
    >>> result = c.add(name='bar',type='python')
    >>> id = result['id']
    >>> result['seq']
    1

    # 控制蛇的方向
    >>> result = c.turn(id=id, d=0, round=-1)

    # 获取地图信息
    >>> m = c.map()

    # 获取实时信息
    >>> info = c.info()
    """
    import doctest
    doctest.testmod()

if __name__=="__main__":
    test()
