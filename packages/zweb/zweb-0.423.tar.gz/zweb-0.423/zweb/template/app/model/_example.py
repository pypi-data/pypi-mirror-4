#coding:utf-8

import _env

from model._db import Model , ModelMc, redis, redis_key


#REDIS_XXX = redis_key.xxx("%s")


# 记得登记表名字 
# vi _table.py
class Xxx(Model):
    pass

if __name__ == "__main__":
    pass
    for i in Xxx.iter():
        print i 
