#coding:utf-8
import _env
from misc import config

import sys
from zweb.server.server_tornado_wsgi import Run
#from zweb.server_tornado import Run

from application import application

from zweb.config_loader import CONFIG_LOADED
for i in CONFIG_LOADED:
    print "loaded config : \n\t%s.py"%i.__file__.rsplit(".",1)[0][len(_env.PREFIX)+1:]

if len(sys.argv)!=1 and sys.argv[1][:5] == '-port':
    PORT = sys.argv[1].split('=')[1]
else:
    PORT = config.PORT

run = Run(PORT, application)

if __name__ == "__main__":
    run()


