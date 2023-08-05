import _env
from collections import defaultdict
import getpass
import socket
from zweb.config_loader import load
from os import mkdir, remove
import sys
from os.path import abspath, join, exists
from shutil import copy2 , rmtree

HOST_USER = defaultdict(set)

#HOST_USER['e1'].add('z32')
HOST_NAME = socket.gethostname()
HOST_USER[HOST_NAME].add(getpass.getuser())

def _host_user_config():
    for user in HOST_USER[HOST_NAME]:

        path = abspath('tmp_config')
        if exists(path):
            rmtree(path)

        mkdir(path)
        sys.path.insert(0, path)
        for from_path , to_path in (
            ('%s/misc/config/default.py'%_env.PREFIX, join(path, 'default.py')) ,
            ('%s/misc/config/_host/%s.py'%(_env.PREFIX, HOST_NAME), join(path, 'host.py')) ,
            ('%s/misc/config/_user/%s.py'%(_env.PREFIX, user), join(path, 'user.py')) ,
        ):
            if exists(from_path):
                if exists(to_path):
                    remove(to_path)
                copy2(from_path, to_path)

        o = load(
            {},
            'default',
            'host' ,
            'user' ,
        )
        sys.path.pop(0)
        yield HOST_NAME, user, o

        rmtree(path)

HOST_USER_CONFIG = list(_host_user_config())

if __name__ == '__main__':
    for host, user, config in host_user_config_iter():
        print host, user , config.HOST

