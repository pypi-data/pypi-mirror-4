#coding:utf-8
import clint
from clint.textui import puts, indent
from optparse import OptionParser, make_option
from os.path import abspath, dirname, join, exists
from os import symlink, chmod, mkdir
from glob import glob
import shutil
import envoy
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def _create(template, name):
    from zweb import template as _template
    path = join(dirname(abspath(_template.__file__)), template)
    name = abspath(name)
    if exists(name):
        print "create failed : %s already exist"%name
    else:
        envoy.run('mkdir %s'%name)
        envoy.run("tar zxvf %s.tgz -C %s"%(path, name))
        print 'create success : \n\t%s\n'%name

option_list = [

    make_option(
        '-a', '--app', dest='app', type="string", nargs=1,
        help='在项目中创建一个app'
    ),
    make_option(
        '-p', '--project', 
        dest='project',
        type="string", nargs=1,
        help='创建一个项目'
    ),
]
parser = OptionParser(option_list=option_list)


def main():
    (option, args) = parser.parse_args()

    if option.project:
        name = option.project
        _create("project", name)
        for i in glob("%s/*.sh"%name): 
            chmod(i, 0755)
        
        import socket
        path = "%s/misc/config/_host/%%s.py"%name
        shutil.copy2( path%"_example", path%socket.gethostname())

        import getpass
        path = "%s/misc/config/_user/%%s.py"%name
        shutil.copy2( path%"_example" , path%getpass.getuser())
    
        print "please edit config then run misc/once/install.py\n\ncd %s;vim misc/config/default.py;./misc/once/install.sh\n"%name
    elif option.app:
        if exists(".app"):
            name = option.app
            _create("app", ".app/%s"%name)
            for i in ("model", "css", "js", "html","view","coffee"):
                if not exists(i):
                    mkdir(i)
                path = "%s/%s"%(i,name)
                if not exists(path):
                    symlink("../.app/%s/%s"%(name, i), path)
            for i in ("config","crontab","lib", "once", "backup", "srv"):
                path = "misc/%s/%s"%(i,name)
                if not exists(path):
                    symlink("../../.app/%s/misc/%s"%(name, i), path)
            path = "../../.app/%s/css/_img"%name
            if not exists(path):
                symlink(path , "css/_img/%s"%name)
            print "please add .app/%s to revision control"%name
            print "please modify misc/boot/app_install.py to import your app %s"%name
        else:
            print "no exist dir .app"
    else:
        parser.print_help()

