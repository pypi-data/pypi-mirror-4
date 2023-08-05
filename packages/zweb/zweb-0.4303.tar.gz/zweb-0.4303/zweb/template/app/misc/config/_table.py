#coding:utf-8
import _env
from os.path import dirname, basename, abspath

MYSQL_DB = basename(dirname(dirname(dirname(abspath(__file__)))))

MYSQL_TABLE = (
   # 用到的表名 , 记得每一行用逗号 , 结尾 
   #'Blog',
)

MYSQL_CONFIG = {
    MYSQL_DB : MYSQL_TABLE
}

