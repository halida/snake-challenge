#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: snake_game
"""
from lib import *
from simple import *
from map.map import Map
from random_wall import RandomWallGen
import db
# 蛇的方向
LEFT, UP, RIGHT, DOWN = range(4)

# 方向对应修改的坐标
DIRECT = (
    (-1, 0), (0, -1), (1, 0), (0, 1)
    )

# 检查hit时的标识
NULL, WALL, GEM, EGG, PORTAL = range(5)

# 游戏状态
INITIAL = 'initial'
WAITFORPLAYER='waitforplayer'
RUNNING='running'
FINISHED='finished'

# 蛇的种类
PYTHON = 'python'
RUBY = 'ruby'

#sprint
SPRINT_ROUND = 5 
SPRINT_STEP = 3 # sprint的时候, 每轮可以走的步数
SPRINT_REST = 20 # sprint之后需要休息的时间

DEFAULT_MAP = 'srcs/map/campain.yml'#'srcs/map/campain.yml'

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
        self.sprint = 0

        # 计算身体
        dx, dy = DIRECT[direction]
        self.body = [
            [(head[0] - dx * i + self.w) % self.w,
             (head[1] - dy * i + self.h) % self.h]
            for i in range(length)]

    def op(self, d):
        if not d: return
        op = d['op']
        if op == 'turn':
            d = d['direction']
            # no turn back
            if (self.direction != d and self.direction % 2 == d % 2): return
            self.direction = d
            
        elif op == 'sprint':
            if self.sprint: return
            self.sprint = SPRINT_ROUND

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

        if self.sprint==0:
            return self.one_step()
        
        if self.sprint > 0:
            self.sprint -= 1
            for i in range(SPRINT_STEP):
                self.one_step()
            if self.sprint == 0:
                self.sprint -= SPRINT_REST

        if self.sprint < 0:
            self.sprint += 1
            return

    def one_step(self):
        """移动一步"""
        if not self.alive: return
        next = self.get_next()
        # 检查是否撞到东西
        what = self.game.check_hit(next)
        # 没有撞到
        if not what:
            self.body.pop(-1)
            self.body.insert(0, next)
            return

        # portal
        if what == PORTAL:
            portal_next = self.game.get_portal_next(next)
            # 检查是否portal对面是蛇
            portal_next_what = self.game.check_hit_snake(portal_next)
            if portal_next_what:
                self.hit_others(next, portal_next_what)
                return
            # 移动头部
            self.body.pop(-1)
            self.body.insert(0, portal_next)
            return

        # 撞死了
        if what not in (GEM, EGG):
            self.hit_others(next, what)
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
            if self.length() < 3:
                self.alive = False
                self.game.log('snake die because of eat wrong type of bean: '+ self.name)
        # 吃完豆子, 再到新的长度..
        self.body.insert(0, next)

    def hit_others(self, next, what):
        self.alive = False
        self.game.log('snake hit and die: '+ self.name)
        # 如果撞到其他蛇的头部, 其他蛇也挂了
        if (isinstance(what, Snake)
            and what.head() == next):
            what.alive = False
            self.game.log('snake hit by others and die: '+ what.name)

    def head(self):
        """获取蛇的头部位置"""
        return self.body[0]

    def length(self):
        """获取蛇的长度"""
        return len(self.body)


class Game():
    """游戏场景"""
    # 记录分数
    def __init__(self,
                 enable_bean=True,
                 enable_wall=True,
                 enable_no_resp_die=True,
                 map=None):
        self.enable_bean = enable_bean
        self.enable_wall = enable_wall
        self.enable_no_resp_die = enable_no_resp_die

        if not map:
            map = Map.loadfile(DEFAULT_MAP)
        self.set_map(map)
        self.start()

    def log(self, msg):
        self.logs.append(msg)

    def user_set_map(self, data):
        if self.status != WAITFORPLAYER:
            return "only can set map when the game state is waitforplayer"

        try:
            m = Map.loaddata(data)
            self.set_map(m)
            self.start()
            return 'ok'
        except Exception as e:
            # if error, fall back to default map
            self.set_map(Map.loadfile(DEFAULT_MAP))
            self.start()
            return 'setmap error: ', str(e)
        
    def set_map(self, map):
        self.map = map
        self.MAX_ROUND = map.meta['round']
        self.wallgen = map.wallgen
        self.portals = map.portals
        self.size = self.w, self.h = map.meta['width'], map.meta['height']

    def start(self):
        '''
        # 因为js没有(), 只好用[]
        self.walls = [[10, i]
                      for i in range(5, 35)]
        '''
        self.logs = []
        self.info = None

        self.walls = [] # to pass unittest
        self.snakes = []
        self.round = 0
        self.snake_op = []
        self.bean_time = 4 # 多少轮会出现一个豆子
        self.eggs = []
        self.gems = []
        self.loop_count = 0
        self.status = WAITFORPLAYER
        #if self.wallgen.can(self):
        if self.enable_wall:
            self.walls = self.wallgen.gen(self)

    def add_snake(self,
                  type=PYTHON,
                  direction=DOWN,
                  head=None,
                  name="unknown"):
        length = self.map.meta['snake_init']
        # 检查蛇类型
        if type not in (PYTHON, RUBY):
            return dict(status='snake type error: %s' % type)
        # 检查蛇数量
        if len(self.snakes) >= self.map.meta['snake_max']:
            return dict(status='no place for new snake.')
        if self.status == FINISHED:
            return dict(stauts='cannot add snake when game is finished.')
        
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
        self.snake_op.append(dict(op='turn', direction=direction))
        # 强制更新info
        self.info = None
        # 返回蛇的顺序, 以及蛇的id(用来验证控制权限)
        return dict(seq=len(self.snakes) - 1, id=snake.id)

    def set_snake(self, n, snake):
        """设置蛇, 调试用"""
        self.snakes[n] = snake
        
    def get_seq(self, id):
        """根据蛇的id获取seq"""
        for i, s in enumerate(self.snakes):
            if s.id == id:
                return i

    def set_snake_op(self, id, round, kw):
        # 获取蛇的seq
        n = self.get_seq(id)
        if n == None:
            return "noid"
        # 检查轮数是否正确
        if round != -1 and self.round != round:
            return "round error, current round: %d" % self.round
        
        if kw['op'] == 'turn':
            kw['direction'] = int(kw['direction'])
            d = kw['direction']
            # 检查direction
            if not 0<=d<=3:
                return "direction error: %d" % d
            # check turn back
            sd = self.snakes[n].direction
        
            self.snake_op[n] = kw
            if (sd != d and sd % 2 == d % 2):
                return "noturnback"
            return 'ok'

        elif kw['op'] == 'sprint':
            self.snake_op[n] = kw
            return 'ok'
        else:
            return 'wrong op: ' + kw['op'] 

    def check_score(self):
        """计算最高分, 保存到历史中"""
        # 只统计活下来的蛇
        lives = [s
                 for s in self.snakes
                 if s.alive]
        if len(lives) <=0: return
        # 计算谁的分数最大
        highest = max(lives, key=lambda s: s.length())
        self.log('game finished, winner: ' + highest.name)
        # 再加到最高分里面去
        db.cursor.execute('insert into scores values(?, ?)', (datetime.datetime.now(), highest.name))
        db.db.commit()

    def scores(self):
        d = date.today()
        today = datetime.datetime(d.year, d.month, d.day)
        dailys =  list(db.cursor.execute('select * from (select name, count(*) as count from scores where time > ? group by name) order by count desc limit 10', (today, )))
        weeklys = list(db.cursor.execute('select * from (select name, count(*) as count from scores where time > ? group by name) order by count desc limit 10', (today - datetime.timedelta(days=7), )))
        monthlys = list(db.cursor.execute('select * from (select name, count(*) as count from scores where time > ? group by name) order by count desc limit 10', (today - datetime.timedelta(days=30), )))
        return dict(dailys=dailys, weeklys=weeklys, monthlys=monthlys)

    def get_map(self):
        return dict(walls=self.walls,
                    portals=self.portals,
                    size=self.size,
                    name=self.map.name,
                    author=self.map.author,
                    )

    def get_info(self):
        if self.info:
            return self.info
        snakes = [dict(direction=s.direction,
                       body=s.body,
                       name=s.name,
                       type=s.type,
                       sprint=s.sprint,
                       length=len(s.body),
                       alive=s.alive)
                  for s in self.snakes
                  ]
        self.info = dict(snakes=snakes,
                         status=self.status,
                         eggs=self.eggs,
                         gems=self.gems,
                         round=self.round,
                         logs=self.logs)
        return self.info

    def step(self):
        """游戏进行一步..."""
        self.logs = []
        self.info = None
        # 如果游戏结束或者waitforplayer, 等待一会继续开始
        if self.loop_count <= 50 and self.status in [FINISHED, WAITFORPLAYER]:
            self.loop_count += 1
            return

        if self.status == FINISHED:
            self.loop_count = 0
            self.start()
            return True

        # 游戏开始的时候, 需要有2条以上的蛇加入.
        if self.status == WAITFORPLAYER:
            if len(self.snakes) < 2: return
            self.status = RUNNING
            self.log('game running.')

        # 首先检查获胜条件:
        # 并且只有一个人剩余
        # 或者时间到
        alives = sum([s.alive for s in self.snakes])
        if alives <= 1 or(self.MAX_ROUND != 0 and self.round > self.MAX_ROUND):
            self.status = FINISHED
            self.loop_count = 0
            self.check_score()
            return True

        # 移动snake
        for i, d in enumerate(self.snake_op):
            snake = self.snakes[i]
            if not snake.alive: continue

            # 如果连续没有响应超过10次, 让蛇死掉
            if d == None and self.enable_no_resp_die:
                self.no_response_snake_die(snake, self.round)

            snake.op(d)
            snake.move()

        # 生成豆子
        if self.map.beangen.can(self):
            beans = self.map.beangen.gen(self)
            self.eggs += beans[0]
            self.gems += beans[1]
        
        #if self.round % self.bean_time == 0:
        #    self.create_bean()

        # next round
        self.round += 1
        self.snake_op = [None, ] * len(self.snakes)
        return True

    def get_portal_next(self, p):
        seq = self.portals.index(p)
        return self.portals[(seq / 2)*2 + ((seq%2)+1)%2 ]
    
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
        if p in self.portals:
            return PORTAL
        return self.check_hit_snake(p)

    def check_hit_snake(self, p):
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
        if snake.no_resp_time >= 5:
            snake.alive = False
            logging.debug('kill no response snake: %d' % \
                         self.snakes.index(snake))
            self.log('kill snake for no response: '+snake.name)
        
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
