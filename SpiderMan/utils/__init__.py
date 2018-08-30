"""一些web服务需要的要程序
全局配置, mysql连接池, scrapy生成
"""
import os
import logging
import configparser
from os.path import isdir
from os.path import join
from os.path import expanduser

HOME_PATH = expanduser('~')
if not isdir(join(HOME_PATH, "SpiderMan")):
    os.makedirs(join(HOME_PATH, "SpiderMan", 'db'))
    os.makedirs(join(HOME_PATH, "SpiderMan", 'project', 'scrapys'))

CONF = """
HOST = '0.0.0.0'
PORT = 8659
MYSQLHOST = ''
MYSQLPORT = 3306
MYSQLUSER = 'root'
MYSQLPASSWORD = ''
LOGGING_LEVE = "DEBUG"
"""


class _SpiderManConf(object):
    """全局配置
    如果mysql == false 默认使用sqllite
    """
    SPIDER_MAN_PATH = join(HOME_PATH, "SpiderMan")
    SPIDER_MAN_SCRAPY_FILE_PATH = join(SPIDER_MAN_PATH, 'project', 'scrapys')
    SPIDER_MAN_CONF_PY = join(SPIDER_MAN_PATH, 'SpiderManConf.ini')

    def __init__(self):
        self.cfg = configparser.ConfigParser()
        if not os.path.isfile(self.SPIDER_MAN_CONF_PY):
            self.MYSQLPORT = 3306
            self.MYSQLHOST = "127.0.0.1"
            self.MYSQLUSER = "root"
            self.MYSQLPASSWORD = ""
            self.LOGGINGLEVEL = "DEBUG"
            self.HOST = "0.0.0.0"
            self.port = 8659
            self.cfg.add_section("mysql")
            self.cfg.add_section("logging")
            self.cfg.add_section("server")
            self.cfg.set("mysql", "port", str(self.MYSQLPORT))
            self.cfg.set("mysql", "host", self.MYSQLHOST)
            self.cfg.set("mysql", "user", self.MYSQLUSER)
            self.cfg.set("mysql", "password", self.MYSQLPASSWORD)
            self.cfg.set("logging", "level", self.LOGGINGLEVEL)
            self.cfg.set("server", "host", self.HOST)
            self.cfg.set("server", "port", str(self.PORT))
            with open(self.SPIDER_MAN_CONF_PY, "w") as f:
                self.cfg.write(f)
        else:

            self.cfg.read(self.SPIDER_MAN_CONF_PY)
            self.MYSQLPORT = self.cfg.getint("mysql", "port")
            self.MYSQLHOST = self.cfg.get("mysql", "host")
            self.MYSQLUSER = self.cfg.get("mysql", "user")
            self.MYSQLPASSWORD = self.cfg.get("mysql", "password")
            self.LOGGINGLEVEL = self.cfg.get("logging", "level")
            self.HOST = self.cfg.get("server", "host")
            self.PORT = self.cfg.get("server", "port")


    def __getattr__(self, item):
        value = {
            "HOST": '0.0.0.0',
            "PORT": 8659,
            "MYSQLHOST": "127.0.0.1",
            "LOGGING_LEVE": "DEBUG",
            "MYSQLPORT": 3306,
            "MYSQLUSER": "root",
            "MYSQLPASSWORD":"",
        }.get(item, None)
        if not value:
            raise ValueError("SpiderManConf missing '{}'".format(item))
        return value

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

SpiderManConf = _SpiderManConf()
logging.basicConfig(level=SpiderManConf.LOGGING_LEVE,
                    format="%(asctime)s - %(name)s - %(levelname)s: %(message)s")


def getIp(domain):
    """get Website ip
    :param domain: Website
    :return Website ip
    """
    import socket
    return socket.getaddrinfo(domain, 'http')[0][4][0]
