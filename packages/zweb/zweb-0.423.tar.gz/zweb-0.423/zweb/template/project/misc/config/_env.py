#coding:utf-8

import sys

if sys.getdefaultencoding() != "utf-8":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(message)s\n',
        datefmt='%H:%M:%S',
    )
    
    import yajl
    import json

    json.dump = yajl.dump
    json.dumps = yajl.dumps
    json.loads = yajl.loads
    json.load = yajl.load



from os.path import dirname, abspath, exists

PWD = abspath(__file__)
PREFIX = None
while True and len(PWD) > 1:
    PWD = dirname(PWD)
    if exists("%s/.app"%PWD) and exists("%s/misc"%PWD):
        PREFIX = PWD

if PREFIX and PREFIX not in sys.path:
    sys.path.insert(0, PREFIX)
