#!/usr/bin/env python
# coding: utf-8

import _env
import time
import subprocess
import sys
from os import makedirs
from os.path import exists , join
from model._db import mysql_config
import envoy
import re

COMM_OPTION = ' -h%s -P%s -u%s -p%s %s '


def backup_table(appname, host, port, name, user, password):
    comm_option = COMM_OPTION % (host, port, user, password, name)

    """
    备份一个表数据的命令实例
    mysqldump --skip-opt --no-create-info 数据库名字 表名 --where="id<2000"
    """
    create_table_option = '--skip-comments --no-data --default-character-set=utf8 --skip-opt --add-drop-table --create-options --quick --hex-blob ' + comm_option

    cmd = 'mysqldump ' + create_table_option
    path = join(_env.PREFIX, 'misc/backup/%s'%appname)

    if not exists(path):
        makedirs(path, 0755)


    r = envoy.run(cmd , timeout=120)
    sql = re.sub( r'(\s+AUTO_INCREMENT\=\d+)', '', r.std_out )
    print path
    with open(join( path, 'mysql.sql'), 'w') as backfile:
        backfile.write(sql)


for appname, item in mysql_config().iteritems():
    host, port, name, user, password = item.get('master').split(':')
    backup_table(appname, host, port, name, user, password)

