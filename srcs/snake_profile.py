#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: snake_profile
用来测试profile功能

profile前数据:
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
  1000000    9.065    0.000    9.065    0.000 snake_game.py:290(check_hit)
   500000    2.525    0.000   15.162    0.000 snake_game.py:225(step)
  1000000    1.897    0.000   12.293    0.000 snake_game.py:66(move)
  1000000    0.834    0.000    0.834    0.000 snake_game.py:58(get_next)
"""
from snake_game import *

def main():
    game = Game((40,20),
                enable_bean=False,
                enable_wall=False,
                enable_no_resp_die=False)
    status, seq, id = game.add_snake(PYTHON, DOWN, (3, 4), 2)
    status, seq, id = game.add_snake(PYTHON, DOWN, (2, 2), 4)
    game.walls = [[i, j] for i in range(5, 19) for j in range(12)]
    for i in range(500):
        game.step()
    
    
if __name__=="__main__":
    for i in range(1000):
        main()
