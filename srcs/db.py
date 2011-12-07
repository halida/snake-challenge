#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: db
"""
import sqlite3
db = sqlite3.connect('tmp/game.db')
cursor = db.cursor()
try:
    cursor.execute('create table scores (time, name)')
    cursor.execute('create index scores_time_index on scores(time)')
except:
    pass


