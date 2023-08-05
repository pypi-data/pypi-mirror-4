#coding:utf-8
from _env import PREFIX

import default
import getpass
import socket
from misc import config

config.DEBUG = True

from zweb.config_loader import load
load(
    vars(config),
    '_host.%s'%socket.gethostname(),
    '_host.%s_dev'%socket.gethostname(),
    '_user.%s'%getpass.getuser(),
    '_user.%s_dev'%getpass.getuser(),
)

