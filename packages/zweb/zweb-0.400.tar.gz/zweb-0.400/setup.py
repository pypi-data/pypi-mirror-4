#coding:utf-8

from setuptools import setup, find_packages 

setup(
    name='zweb',
    version="0.400",
    description="A web site framework",
    author="zuroc 张沈鹏",
    author_email="zsp042@gmail.com",
    packages = ['zweb'],
    zip_safe=False,
    include_package_data=True,
    install_requires = [
        'zorm>=0.03',
        'tornado>=2.3',
        'mako',
        'clint',
        'cherrypy>=3.2.2',
        'weberror>=0.10.3',
        'envoy',
        'supervisor',
    ],
    entry_points = {
        'console_scripts': [
            'zweb=zweb.script:main',
        ],
    },
)

