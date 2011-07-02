#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: snake_game
"""
from lib import *
from simple import *
from map.map import Map
from random_wall import RandomWallGen
import uuid


# 蛇的方向
LEFT, UP, RIGHT, DOWN = range(4)

# 方向对应修改的坐标
DIRECT = (
    (-1, 0), (0, -1), (1, 0), (0, 1)
    )

# 检查hit时的标识
NULL, WALL, GEM, EGG = range(4)

# 游戏状态
INITIAL = 'initial'
WAITPLAYER='waitplayer'
RUNNING='running'
FINISHED='finished'

# 蛇的种类
PYTHON = 'python'
RUBY = 'ruby'


class Snake():
    def __init__(self, game, type, direction, head, length, name=""):
        """设置snake
        """
        self.game = game
        self.type = type
        self.name = name
        self.w, self.h = self.game.size
        self.id = uuid.uuid4().hex
        
        self.alive = True
        self.direction = direction

        # 计算身体
        dx, dy = DIRECT[direction]
        self.body = [
            [(head[0] - dx * i + self.w) % self.w,
             (head[1] - dy * i + self.h) % self.h]
            for i in range(length)]

    def turn(self, d):
        """控制蛇的方向"""
        self.direction = d

    def get_next(self):
        """获取蛇下一个移动到的位置"""
        head = self.body[0]
        dx, dy = DIRECT[self.direction]
        next = [(head[0] + dx) % self.w,
                (head[1] + dy) % self.h]
        return next

    def move(self):
        """移动蛇"""
        if not self.alive: return

        next = self.get_next()
        # 检查是否撞到东西
        what = self.game.check_hit(next)
        # 没有撞到
        if not what:
            self.body.pop(-1)
            self.body.insert(0, next)
            return

        # 撞死了
        if what not in (GEM, EGG):
            self.alive = False
            # 如果撞到其他蛇的头部, 其他蛇也挂了
            if (isinstance(what, Snake)
                and what.head() == next):
                what.alive = False
            return

        # 吃掉豆子
        if what == EGG:
            self.game.eggs.remove(next)
        elif what == GEM:
            self.game.gems.remove(next)
                
        # 吃错了就要减少长度
        if ((what == EGG and self.type == RUBY) or
            (what == GEM and self.type == PYTHON)):
            self.body.pop(-1)
            self.body.pop(-1)
            # 足够短就被饿死了..
            if self.length() <= 3:
                self.alive = False

        # 吃完豆子, 再到新的长度..
        self.body.insert(0, next)
                

    def head(self):
        """获取蛇的头部位置"""
        return self.body[0]

    def length(self):
        """获取蛇的长度"""
        return len(self.body)


class Game():
    """游戏场景"""
    # 记录分数
    scores = [('AAA', i)
              for i in range(1, 10)]

    def __init__(self, size=(50, 25),
                 enable_bean=True,
                 enable_wall=True,
                 enable_no_resp_die=True,
                 map=None):
        self.size = self.w, self.h = size
        self.enable_bean = enable_bean
        self.enable_wall = enable_wall
        self.enable_no_resp_die = enable_no_resp_die

        if not map:
            map = Map.load('srcs/map/sample.map')
        self.setMap(map)
        self.restart()

    def setMap(self, map):
        self.wallgen = map.wallgen
        #self.wallgen = RandomWallGen() #SimpleWallGen()
        self.beangen = map.beangen

    def restart(self):
        '''
        # 因为js没有(), 只好用[]
        self.walls = [[10, i]
                      for i in range(5, 35)]
        '''
        self.walls = [] # to pass unittest
        self.snakes = []
        self.round = 0
        self.snake_op = []
        self.bean_time = 4 # 多少轮会出现一个豆子
        self.eggs = []
        self.gems = []        
        self.status = WAITPLAYER
        #if self.wallgen.can(self):
        if self.enable_wall:
            self.walls = self.wallgen.gen(self)

    def add_snake(self,
                  type=PYTHON,
                  direction=DOWN,
                  head=None,
                  length=5,
                  name="AAA"):
        # 检查蛇类型
        if type not in (PYTHON, RUBY):
            return 'snake type error: %s' % type, None, None
        # 检查蛇数量
        if len(self.snakes) >= 10:
            return 'no place for new snake.', None, None
        
        # 随机生成蛇的位置
        d = DIRECT[direction]
        if not head:
            while True:
                # 蛇所在的地点不能有东西存在..
                next = self.get_empty_place()
                for i in range(length + 1):
                    body = [(next[0] - d[0] * i) % self.w,
                            (next[1] - d[1] * i) % self.h]
                    if self.check_hit(body):
                        break
                # 如果检查没有发现任何一点重合, 就用改点了.
                else:
                    head = [(next[0] - d[0]) % self.w,
                            (next[1] - d[1]) % self.h]
                    break
        # 生成蛇
        snake = Snake(self, type, direction, head, length, name)
        self.snakes.append(snake)
        self.snake_op.append(direction)
        # 返回蛇的顺序, 以及蛇的id
        return None, len(self.snakes) - 1, snake.id

    def set_snake(self, n, snake):
        """设置蛇, 调试用"""
        self.snakes[n] = snake
        
    def get_seq(self, id):
        """根据蛇的id获取seq"""
        for i, s in enumerate(self.snakes):
            if s.id == id:
                return i

    def turn_snake(self, n, d, round):
        # 获取蛇的seq
        if type(n) in (str, unicode):
            n = self.get_seq(n)
            if n == None:
                return "noid"
        # 检查轮数是否正确
        if round != -1 and self.round != round:
            return "round error, current round: %d" % self.round
        # 检查direction
        if not 0<=d<=3:
            return "direction error: %d" % d
        # check turn back
        sd = self.snakes[n].direction
        if (sd != d and sd % 2 == d % 2):
            return "noturnback"
        
        self.snake_op[n] = d
        return 'ok'

    def check_score(self):
        """计算最高分, 保存到历史中"""
        # 只统计活下来的蛇
        lives = [s
                 for s in self.snakes
                 if s.alive]
        if len(lives) <=0: return
        # 计算谁的分数最大
        highest = max(lives, key=lambda s: s.length())
        # 再加到最高分里面去
        self.scores.append(
            (highest.name, highest.length()))
        self.scores.sort(key= lambda d: d[1])
        # 只统计10个
        if len(self.scores) > 10:
            self.scores.pop(0)

    def step(self):
        """游戏进行一步..."""
        # 游戏结束就不进行了.
        if self.status == FINISHED: return
                
        # 是否更新墙
        #if self.wallgen.can(self):
        #    self.walls = self.wallgen.gen(self)
            
        #if self.status == INITIAL:
        #	self.status = WAITPLAYER

        # 游戏开始的时候, 需要有2条以上的蛇加入.
        if self.status == WAITPLAYER:
            if len(self.snakes) < 2: return
            self.status = RUNNING

        # 获胜条件:
        # 并且只有一个人剩余
        # 或者时间到
        alives = sum([s.alive for s in self.snakes])
        if alives <= 1 or self.round > 600:
            self.status = FINISHED
            self.check_score()
            return

        # 移动snake
        for i, d in enumerate(self.snake_op):
            snake = self.snakes[i]
            if not snake.alive: continue
            if d == None:
                # 如果连续没有响应超过3次, 让蛇死掉
                if self.enable_no_resp_die:
                    self.no_response_snake_die(snake, self.round)
            else:
                snake.turn(d)
            snake.move()

        # 生成豆子
        if self.beangen.can(self):
            beans = self.beangen.gen(self)
            self.eggs += beans[0]
            self.gems += beans[1]
        
        #if self.round % self.bean_time == 0:
        #    self.create_bean()

        # next round
        self.round += 1
        self.snake_op = [None, ] * len(self.snakes)
    
    def create_bean(self):
        """生成豆子
        """
        if not self.enable_bean: return

        pos = self.get_empty_place()
        # 随机掉落豆子的种类
        if random.randint(0, 1):
            # 有豆子数量限制
            if len(self.gems) > 10: return
            self.gems.append(pos)
        else:
            if len(self.eggs) > 10: return
            self.eggs.append(pos)
    def check_hit(self, p):
        """检查p和什么碰撞了, 返回具体碰撞的对象"""
        if p in self.walls:
            return WALL
        if p in self.eggs:
            return EGG
        if p in self.gems:
            return GEM
        for snake in self.snakes:
            if p in snake.body:
                return snake

    def get_empty_place(self):
        """
        随机获取一个空的位置
        可能是性能陷阱?
        """
        while True:
            p = [random.randint(0, self.w-1),
                 random.randint(0, self.h-1)]
            # 不要和其他东西碰撞
            if self.check_hit(p):
                continue
            return p

    def alloped(self):
        """
        判断是否所有玩家都做过操作了
        """
        oped = [
            (not s.alive or op != None)
            for op, s in zip(self.snake_op,
                             self.snakes)]
        return all(oped)

    def no_response_snake_die(self, snake, round):
        """
        如果连续没有响应超过3次, 让蛇死掉
        round是没有响应的轮数(用来检查是否连续没有响应)
        
        """
        # 初始化缓存
        if (not hasattr(snake, 'no_resp_time') or
            snake.no_resp_round != round - 1):
            snake.no_resp_time = 1
            snake.no_resp_round = round
            return
        # 次数更新
        snake.no_resp_time += 1
        snake.no_resp_round = round            
        # 判断是否没有响应时间过长
        if snake.no_resp_time >= 3:
            snake.alive = False
            logging.debug('kill no response snake: %d' % \
                         self.snakes.index(snake))
        
def test():
    """
    # 初始化游戏
    >>> game = Game((20,20),
    ...     enable_bean=False,
    ...     enable_wall=False,
    ...     enable_no_resp_die=False)
    
    >>> status, seq, id = game.add_snake(PYTHON, DOWN, (3, 4), 2)
    >>> status, seq, id = game.add_snake(PYTHON, DOWN, (18, 2), 4)
    >>> game.step()
    >>> game.status == RUNNING
    True

    # 基本的移动
    >>> game.snakes[1].alive
    True
    >>> game.step()
    >>> game.snakes[0].head()
    [3, 6]

    # 改变方向
    >>> game.turn_snake(0, LEFT, -1)
    'ok'
    >>> game.step()
    >>> game.snakes[0].head()
    [2, 6]
    >>> game.snakes[0].alive
    True

    # 超出地图会回转
    >>> game.step()
    >>> game.snakes[0].head()
    [1, 6]
    >>> game.step()
    >>> game.snakes[0].head()
    [0, 6]
    >>> game.step()
    >>> game.snakes[0].head()
    [19, 6]

    # 撞到其他snake会挂掉
    >>> game.set_snake(1, Snake(game, PYTHON, DOWN, (18, 7), 5))
    >>> game.step()
    >>> game.snakes[0].alive
    False
    >>> status, seq, id = game.add_snake()

    # 吃豆子
    >>> game.eggs.append([18, 9])
    >>> game.step()
    >>> len(game.eggs)
    0
    >>> game.snakes[1].length()
    6

    # python吃了gem会缩短(拉肚子)
    >>> s = game.snakes[1]
    >>> pos = s.get_next()
    >>> game.gems.append(pos)
    >>> game.step()
    >>> s.length()
    5
    >>> game.gems
    []

    # 缩短过度会死掉
    >>> s.body = s.body[:5]
    >>> pos = s.get_next()
    >>> game.gems.append(pos)
    >>> game.step()
    >>> s.alive
    False

    # 2条蛇头部相撞, 都死掉
    >>> game.set_snake(0, Snake(game, PYTHON, DOWN, (18, 6), 5))
    >>> game.set_snake(1, Snake(game, PYTHON, LEFT, (19, 7), 5))
    >>> game.step()
    >>> game.snakes[0].alive
    False
    >>> game.snakes[1].alive
    False

    # 算分
    >>> for s in game.snakes: s.alive = False
    >>> result = game.add_snake(name='no')
    >>> game.step()
    >>> game.status
    'finished'
    >>> ('no', 5) in game.scores
    True
    """
    import doctest
    doctest.testmod()

def main():
    test()
    
if __name__=="__main__":
    main()
