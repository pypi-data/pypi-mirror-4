#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _host_user import HOST_USER_CONFIG 
from _env import PREFIX

import re
from mako.template import Template
from os import mkdir
from os.path import join, dirname, exists, isdir

_CONFIG_DIR = join(PREFIX, 'misc/config/nginx')
with open(join(dirname(__file__),"nginx.conf")) as conf:
    tmpl = conf.read()
T = Template(tmpl)


for host, user, config in HOST_USER_CONFIG:
    CONFIG_DIR = join(_CONFIG_DIR, host)
    
    if not exists(CONFIG_DIR):
        mkdir(CONFIG_DIR)
    port_range = range(config.PORT, config.PORT+config.PROCESS_NUM)
    conf = T.render(
        host=config.HOST,
        name=config.HOST.replace(".","_"),
        ports=port_range,
        prefix=PREFIX,
        host_css_js = config.HOST_CSS_JS,
        host_dev_prefix = config.HOST_DEV_PREFIX,
    )

    with open(join(CONFIG_DIR, '%s.conf' % user),'w') as f:
        f.write(conf)


print('created nginx configure files at %s' % _CONFIG_DIR)

