"""一些web服务需要的要程序
全局配置, mysql连接池, scrapy生成
"""
import sys
import os
from os.path import isdir
from os.path import join
from os.path import expanduser
from importlib import import_module

HOME_PATH = expanduser('~')
if not isdir(join(HOME_PATH, "SpiderMan")):
    os.makedirs(join(HOME_PATH, "SpiderMan", 'db'))
    os.makedirs(join(HOME_PATH, "SpiderMan", 'project', 'scrapys'))

CONF = """
MYSQL = False
SQLLITE = True
HOST = '0.0.0.0'
PORT = 8659
MYSQLHOST = ''
MYSQLUSER = ''
MYSQLPASSWORD = ''
"""


class SpiderManConf(object):
    """全局配置
    如果mysql == false 默认使用sqllite
    """
    SPIDER_MAN_PATH = join(HOME_PATH, "SpiderMan")
    SPIDER_MAN_DB_PATH = join(SPIDER_MAN_PATH, 'db', 'SpiderMan.db')
    SPIDER_MAN_SCRAPY_FILE_PATH = join(SPIDER_MAN_PATH, 'project', 'scrapys')
    SPIDER_MAN_CONF_PY = join(SPIDER_MAN_PATH, 'SpiderManConf.py')
    if not os.path.isfile(SPIDER_MAN_CONF_PY):
        with open(SPIDER_MAN_CONF_PY, 'w') as fp:
            fp.write(CONF)
        MYSQL = False
        SQLLITE = True
        HOST = '0.0.0.0'
        PORT = 8659
        MYSQLHOST = ''
        MYSQLUSER = ''
        MYSQLPASSWORD = ''
    else:
        sys.path.append(SPIDER_MAN_PATH)
        obj = import_module('SpiderManConf')
        MYSQL, SQLLITE, HOST, PORT = obj.MYSQL, obj.SQLLITE, obj.HOST, obj.PORT
        MYSQLHOST, MYSQLUSER, MYSQLPASSWORD = obj.MYSQLHOST, obj.MYSQLUSER, obj.MYSQLPASSWORD

    SCRAPY_SETUP_CODE = """# -*- coding:utf-8 -*-
# create for SpiderMan
from setuptools import setup, find_packages
setup(
    name="%(name)s",
    version="%(version)s",
    package_data={'':['*.*']},
    packages=find_packages(),
    entry_points={'scrapy':['settings=%(name)s.settings']}
)
    """



def getIp(domain):
    """get Website ip
    :param domain: Website
    :return Website ip
    """
    import socket
    return socket.getaddrinfo(domain, 'http')[0][4][0]
