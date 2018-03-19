# -*- coding:utf-8 -*-
import os
import sys
from os.path import (
    expanduser, isdir, join
)
from importlib import import_module

home_path = expanduser('~')
if not isdir(join(home_path, "SpiderMan")):
    os.mkdir(join(home_path, "SpiderMan"))
if not isdir(join(home_path, "SpiderMan", 'project')):
    os.mkdir(join(home_path, "SpiderMan", 'project'))
if not isdir(join(home_path, "SpiderMan", 'project', 'scrapys')):
    os.mkdir(join(home_path, "SpiderMan", 'project', 'scrapys'))
if not isdir(join(home_path, "SpiderMan", 'db')):
    os.mkdir(join(home_path, "SpiderMan", 'db'))

conf = """
MYSQL = False
SQLLITE = True
HOST = '0.0.0.0'
PORT = 8659
MYSQLHOST = ''
MYSQLUSER = ''
MYSQLPASSWORD = ''
"""


class SpiderManConf(object):

    SPIDER_MAN_PATH = join(home_path, "SpiderMan")
    SPIDER_MAN_DB_PATH = join(SPIDER_MAN_PATH, 'db', 'SpiderMan.db')
    SPIDER_MAN_SCRAPY_FILE_PATH = join(SPIDER_MAN_PATH, 'project', 'scrapys')
    SPIDER_MAN_CONF_PY = join(SPIDER_MAN_PATH, 'SpiderManConf.py')
    if not os.path.isfile(SPIDER_MAN_CONF_PY):
        with open(SPIDER_MAN_CONF_PY, 'w') as f:
            f.write(conf)
        MYSQL = False
        SQLLITE = True
        HOST = '0.0.0.0'
        PORT = 8659
        MYSQLHOST = ''
        MYSQLUSER = ''
        MYSQLPASSWORD = ''
    else:
        sys.path.append(SPIDER_MAN_PATH)
        o = import_module('SpiderManConf')
        MYSQL, SQLLITE, HOST, PORT = o.MYSQL, o.SQLLITE, o.HOST, o.PORT
        PORT, MYSQLHOST, MYSQLUSER, MYSQLPASSWORD  = o.PORT, o.MYSQLHOST, o.MYSQLUSER, o.MYSQLPASSWORD
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
SpiderManConf()

def getIp(domain):
    """get Website ip
    :param domain: Website
    :return Website ip
    """
    import socket
    return socket.getaddrinfo(domain, 'http')[0][4][0]
