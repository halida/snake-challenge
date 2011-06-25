#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: player
"""
import random

class Player():
    def __init__(self, debug):
        self.name = 'Player'
        self.type = 'python'
        self.debug = debug
    
    def init(self, seq, map):
        pass
        
    def turn(self, info):
        return random.randint(0, 3)
        
        