#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: convert image to snake challenge map, require PIL
"""

import sys
import Image

def color2map(color):
    if color[0] < 128 and color[1] < 128 and color[2] < 128:
        return 'W'
    elif color[0] > 128 and color[1] < 128 and color[2] < 128:
        return 'X'
    elif color[0] < 128 and color[1] < 128 and color[2] > 128:
        return 'S'
    else:
        return '.'

def image2map(file, size=None):
    map = []
    img = Image.open(file, 'r').convert("RGB")
    
    if size is not None:
        img = img.resize(size)
        
    data = img.load()
    for i in range(img.size[1]):
        mapscan = []
        for j in range(img.size[0]):
            color = data[j,i]
            mapscan.append(color2map(color))
        map.append(mapscan)
    return map
    
def mapconfigs():
    cfgs = ['author','version','name','snakelength','size','food','maxfoodvalue']
    meta = {}
    for cfg in cfgs:
        sys.stdout.write(cfg + ": ")
        input = sys.stdin.readline()
        meta[cfg] = input
    return meta
    
def writetofile(meta, map, file):
    with open(file, 'w') as f:
        for mk,mv in meta.items():
            f.write(mk+": "+mv)
        f.write("map:\n")
        for y in map:
            for x in y:
                f.write(x)
            f.write("\n")

def tosize(value):
    d = value.strip().split('x')
    return (int(d[0]), int(d[1]))

if __name__ == '__main__':
    meta = mapconfigs()
    try:
        size = tosize(meta['size'])
    except Exception:
        size = None
    print size
    map = image2map(sys.argv[1], size)
        
    writetofile(meta, map, sys.argv[2])