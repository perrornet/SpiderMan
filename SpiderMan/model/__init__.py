# -*- coding:utf-8 -*-
import os
from os.path import (
    expanduser, isdir, join
)

home_path = expanduser('~')
if not isdir(join(home_path, "SpiderMan")):
    os.mkdir(join(home_path, "SpiderMan"))
if not isdir(join(home_path, "SpiderMan", 'project')):
    os.mkdir(join(home_path, "SpiderMan", 'project'))
if not isdir(join(home_path, "SpiderMan", 'project', 'scrapys')):
    os.mkdir(join(home_path, "SpiderMan", 'project', 'scrapys'))
if not isdir(join(home_path, "SpiderMan", 'db')):
    os.mkdir(join(home_path, "SpiderMan", 'db'))


class SpiderManConf(object):
    MYSQL = False
    SQLLITE = True
    HOST = '0.0.0.0'
    PORT = 8659
    MYSQLHOST = ''
    MYSQLUSER = ''
    MYSQLPASSWORD = ''
    SPIDER_MAN_PATH = join(home_path, "SpiderMan")
    SPIDER_MAN_DB_PATH = join(SPIDER_MAN_PATH, 'db', 'SpiderMan.db')
    SPIDER_MAN_SCRAPY_FILE_PATH = join(SPIDER_MAN_PATH, 'project', 'scrapys')

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
