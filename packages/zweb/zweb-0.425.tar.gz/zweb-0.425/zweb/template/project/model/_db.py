#coding:utf-8
import _env
from misc import config
import zorm.config as zorm_config

from misc.config import DEBUG
zorm_config.DEBUG = DEBUG


from redis import StrictRedis
from misc.config import REDIS_CONFIG

zorm_config.redis = redis = StrictRedis(**REDIS_CONFIG)



from zorm.mc_connection import init_mc
from misc.config import MEMCACHED_ADDR , DISABLE_LOCAL_CACHED

mc = init_mc(
    memcached_addr=MEMCACHED_ADDR,
    disable_local_cached=DISABLE_LOCAL_CACHED
)

zorm_config.mc = mc

from zorm import sqlstore

def mysql_config():
    from glob import glob
    from misc.config import MYSQL_HOST , MYSQL_PORT , MYSQL_USER , MYSQL_PASSWD , MYSQL_PREFIX
    from os.path import dirname, abspath, join, exists, basename
    import sys
    sqlfarm = {}
    for i in glob('%s/.app/*'%_env.PREFIX):
        if '.' in basename(i):
            continue
        path = join(i, 'misc/config/_table.py')
        if exists(path):
            if '__init__' in sys.modules:
                del sys.modules['__init__']
            if '_table' in sys.modules:
                del sys.modules['_table']
            d = dirname(path)
            sys.path.insert(0, d)
            c = __import__('__init__')
            sys.path.pop(0)

            for mysql_db, mysql_table in c.MYSQL_CONFIG.iteritems():
                db = '%s_%s'%(MYSQL_PREFIX, mysql_db)

                sqlfarm[basename(i)] = {
                    'master': '%s:%s:%s:%s:%s' % ( MYSQL_HOST, MYSQL_PORT, db, MYSQL_USER, MYSQL_PASSWD),
                    'tables': mysql_table,
                }

    return sqlfarm

_sqlstore = sqlstore.SqlStore(db_config=mysql_config(), charset='utf8')

def db_by_table(table):
    return _sqlstore.get_db_by_table(table)

zorm_config.db_by_table = db_by_table



from zorm.model import Model, ModelMc
from zorm.redis import redis, redis_key




if __name__ == '__main__':
    pass
    print mysql_config()

