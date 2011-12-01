#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: lib
"""
import sys, os
import time, logging, json, random, uuid, datetime
from datetime import date

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")


class Clock():
    """一个分时器，限制刷新率
    >>> c = Clock(20) # fps
    >>> c.tick(block=False)
    """
    def __init__(self, fps):
        self.set_fps(fps)

    def set_fps(self, fps):
        self.fps = fps
        self.interval = 1.0/float(fps)
        self.pre = time.time()

    def tick(self, block=True):
        """
        检查是否到了时间
        """
        mid = time.time() - self.pre
        if  mid < self.interval:
            if block:
                time.sleep(self.interval - mid)
            else:
                return
        self.pre = time.time()
        return True
