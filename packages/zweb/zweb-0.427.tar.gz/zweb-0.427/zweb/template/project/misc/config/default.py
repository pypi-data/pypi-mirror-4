#coding:utf-8
import _env


def pre_config(o):

    o.HOST = 'z32e1.tk'
    o.SITE_NAME   = '42区'
    o.SITE_SLOGO  = "找到给你答案的人"


    o.DEBUG = False
    o.PORT = 42001
    o.PROCESS_NUM = 4
    

    o.MYSQL_HOST = '127.0.0.1'
    o.MYSQL_PORT = '3306'
    o.MYSQL_USER = 'zweb'
    o.MYSQL_PASSWD = '42qudev'
    o.MYSQL_PREFIX = o.MYSQL_USER

    o.HOST_DEV_PREFIX = "dev-"


    o.MEMCACHED_ADDR = (
        '127.0.0.1:11211',

    )
    o.DISABLE_LOCAL_CACHED = False

    o.REDIS_CONFIG = dict(
#        unix_socket_path = "/tmp/redis.sock"
        host = 'localhost', 
        port = 6379, 
        db   = 0
    )

def post_config(o):
    o.SITE_URL = "//%s"%o.HOST
    o.SITE_HTTP = "http:%s"%o.SITE_URL

    # 注意：备份路径只为数据备份准备，而不是表备份
    o.BACKUP_PATH = '/mnt/backup/%s'%o.HOST

    # css js 静态文件的域名
    o.HOST_CSS_JS = 's.%s'%o.HOST
    o.URL_FS =  'http://%s'%o.HOST_CSS_JS

