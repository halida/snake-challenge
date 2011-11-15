#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: main
"""
from bottle import route, run
from bottle import template

from bottle import static_file
@route('/static/:filename')
def server_static(filename):
    return static_file(filename, root='public')

@route('/')
def index():
    return template('index')

run(host='localhost', port=8080)
