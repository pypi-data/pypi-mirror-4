#!/usr/bin/env python
# coding: utf-8

import _env
import time
import subprocess
import sys
from model._db import mysql_config
from misc.config import BACKUP_PATH

def backup_data(appname, host, port, name, user, password):
    comm_option = COMM_OPTION % (host, port, user, password, name)

    """
    备份一个表数据的命令实例
    mysqldump --skip-opt --no-create-info 数据库名字 表名 --where="id<2000"
    """
    create_table_option = ' --no-create-info --quick --default-character-set=utf8 --skip-opt --hex-blob '+comm_option

    cmd = 'mysqldump ' + create_table_option
    print cmd
    with open(join(BACKUP_PATH, 'data_%s_%s.sql'%(appname,int(time.time()))), 'w') as backfile:
        subprocess.Popen(
            cmd.split(),
            stdout=backfile
        )

def backup_main():
    for appname,item in mysql_config().iteritems():
        host, port, name, user, password = item['master'].split(':')
        backup_data(appname, host, port, name, user, password)

if __name__ == '__main__':
    from os import makedirs
    from os.path import exists
    if not exists(BACKUP_PATH):
        makedirs(BACKUP_PATH,0755)
    backup_main()

print('backup data complete.')

