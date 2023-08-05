#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 初始化python的查找路径
import _env
import getpass
import socket
from zweb.config_loader import load

load(
    vars(),
    'default', 
    '_host.%s' % socket.gethostname(),
    '_user.%s' % getpass.getuser(),
)


