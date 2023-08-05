#coding:utf-8

def pre_config(o):
    from _table import MYSQL_CONFIG
 
    o.MYSQL_CONFIG = MYSQL_CONFIG

def post_config(o):
    pass
