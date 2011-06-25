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
        room = int(data['room'])
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
            return self.add(data['name'], data['type'])
        elif op == 'turn':
            return self.turn(data['id'], data['direction'],data['round'])
        elif op == 'map':
            return self.map()
        elif op == 'info':
            return self.info()
        elif op == 'history':
            return self.history()
        elif op == 'scores':
            return self.scores()

    def add(self, name, type):
        """
        >>> c = Controller(Game())
        >>> c.add('p1', 'python') ['seq']
        0
        >>> c.add('r1', 'ruby') ['seq']
        1
        """
        status, seq, id = self.game.add_snake(type=type, name=name)
        if status:
            return dict(status=status)
        else:
            return dict(seq=seq, id=id)

    def turn(self, id, d, round):
        status = self.game.turn_snake(id, int(d), int(round))
        return dict(status=status)

    def map(self):
        """
        >>> c = Controller(Game())
        >>> result = c.map()
        """
        return dict(walls=self.game.walls,
                    size=self.game.size)

    def scores(self):
        """
        >>> c = Controller(Game())
        >>> result = c.scores()
        """
        return self.game.scores

    def info(self):
        """
        >>> c = Controller(Game())
        >>> result = c.info()
        """
        g = self.game
        snakes = [dict(direction=s.direction,
                       body=s.body,
                       name=s.name,
                       type=s.type,
                       alive=s.alive)
                  for s in g.snakes
                  ]
        info = dict(snakes=snakes,
                    status=g.status,
                    eggs=g.eggs,
                    gems=g.gems,
                    round=g.round)
        return info

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
