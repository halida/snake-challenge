#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: pygame_show
用pygame来显示逻辑..
"""
from lib import *
import pygame

snake_colors = [(0xa5, 0xc9, 0xe7), (0x08, 0x46, 0x7b), (0x3e, 0x9b, 0xe9), (0x88, 0xdb, 0x99), (0x0e, 0x74, 0x83), (0x85, 0xf5, 0x6b), (0xa5, 0xc9, 0xe7), (0x0a, 0x48, 0x46), (0x3a, 0xe7, 0x12), (0x88, 0xdb, 0x99), (0xf3, 0xf0, 0x0a), (0x0d, 0xb0, 0x2c)]


SIZE = 10
class Shower():
    def __init__(self, map):
        pygame.init()
        self.font = pygame.font.SysFont('sans', 12)
        self.set_map(map)

    def set_map(self, map):
        self.map = map
        size = self.map['size']
        self.screen = pygame.display.set_mode(
            (size[0]*SIZE + 100,
             size[1]*SIZE))

    def flip(self, info):
        # 退出判断
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        size = SIZE
        gem_color = (100,0,0)
        egg_color = (100,100,0)
        portal_color = (100, 0, 100)
        def drawRect(c, x, y, w, h):
            pygame.draw.rect(self.screen, c,
                             pygame.Rect(x, y, w, h))
        # draw map background
        self.screen.fill((200,200,200))
        
        # snakes
        y = 10
        for i, s in enumerate(info['snakes']):
            color = snake_colors[i]

            for dot in s['body']:
                drawRect(color,
                         dot[0] * size,
                         dot[1] * size,
                         size, size)
            # head
            dot = s['body'][0]
            hcolor = egg_color if s['type'] == 'python' else gem_color
            drawRect(hcolor,
                     dot[0] * size + 2,
                     dot[1] * size + 2,
                     size-4, size-4)

            # snake info
            drawRect(color,
                     self.map['size'][0]*size + 10, y, 
                     size, size)
            # text
            sur = self.font.render(s['name'], True, (0,0,0))
            self.screen.blit(sur,
                             (self.map['size'][0]*size + 30, y))
            y += size + 10
                
        # beans
        for bean in info['eggs']:
            drawRect(egg_color,
                     bean[0] * size,
                     bean[1] * size,
                     size, size)
        for bean in info['gems']:
            drawRect(gem_color,
                      bean[0] * size,
                      bean[1] * size,
                      size, size)
        
        # walls
        for wall in self.map['walls']:
            drawRect((0,0,0),
                     wall[0] * size,
                     wall[1] * size,
                     size, size)

        # portals
        for b in self.map['portals']:
            drawRect(portal_color,
                     b[0] * size,
                     b[1] * size,
                     size, size)

        pygame.display.flip()


def pygame_testai(ais):
    """
    输入ai列表, 跑一个pygame的测试游戏看看
    """
    from snake_game import Game
    from game_controller import Controller
    
    game = Game()
    c = Controller(game)
    m = c.map()
    for ai in ais:
        ai.setmap(m)
        result = c.add(ai.name, ai.type)
        ai.seq = result['seq']
        ai.id = result['id']

    clock = Clock(3)
    s = Shower(m)

    while True:
        clock.tick()
        
        info = c.info()
        for ai in ais:
            d = ai.onprocess(info)
            c.turn(ai.id, d, game.round)
        game.step()

        s.flip(info)


def main():
    from ai_simple import AI
    ais = [AI() for i in range(20)]
    pygame_testai(ais)

    
if __name__=="__main__":
    main()
