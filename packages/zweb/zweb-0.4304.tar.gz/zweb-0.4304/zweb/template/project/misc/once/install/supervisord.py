# coding:utf-8

from _host_user import HOST_USER_CONFIG
import _env
from os import mkdir
from os.path import abspath, dirname, basename, join, exists

_CONFIG_DIR = join(_env.PREFIX, 'misc/boot','supervisor')

for host, user, o in HOST_USER_CONFIG:
    CONFIG_DIR = join(_CONFIG_DIR, host)

    prjname = basename(_env.PREFIX)
    online = join(_env.PREFIX, 'misc/boot','online.py')

    if not exists(CONFIG_DIR):
        mkdir(CONFIG_DIR)


    port = str(o.PORT)
    procsnum = o.PROCESS_NUM
    srv_name = prjname+'_'+user
    conf = '''[program:%s]
command=sudo -u %s python %s -port=%s%%(process_num)02d
process_name=%%(program_name)s_%%(process_num)02d
directory=.
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/%s-%%(process_num)02d.log
stdout_logfile_maxbytes=1024MB
stdout_logfile_backups=512
stdout_capture_maxbytes=1MB
stdout_events_enabled=false
loglevel=warn
numprocs_start=%s
numprocs=%d

''' % (
        srv_name, 
        user,
        online,  
        port[:-2], 
        srv_name,
        port[-2:], 
        procsnum
)

    f = open(join(CONFIG_DIR, '%s.conf' % user), 'w')
    f.write(conf)
    f.close()

print('created supervisor configure file at %s' % _CONFIG_DIR)

