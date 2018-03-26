# -*- coding:utf-8 -*-
import re
import getpass
import hashlib
from tornado.log import app_log
from SpiderMan.utils import SpiderManConf
from SpiderMan.models_sql import sum_sql
from SpiderMan.server.web import models
from SpiderMan.server.web.models import User


def input_user(msg=None):
    if not msg:
        print('Registered admin account')
    else:
        print(msg)
    username = input("Please enter the admin account:")
    user = User.getOne(User.username == username)
    if user is not None:
        return input_user("The user has already existed")
    password = getpass.getpass("Please enter the password for the admin:")
    if not password.strip():
        print("The password is empty!")
        return input_user()

    a = lambda x: re.findall(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', x)
    while 1:
        email = input("Please enter the admin email:")
        if a(email):
            break
        print("input email error")
    return username, hashlib.md5(password.encode()).hexdigest(), email


def create_database():
    """创建数据库以及表"""
    models.get_datebase('mysql').execute_sql("CREATE DATABASE {}".format('SpiderMan'))
    [models.get_datebase().execute_sql(sql) for sql in sum_sql]
    # 创建数据库表
    username, password, email = input_user()
    User.create(username=username, password=password, email=email, isadmin=True).save()


def create_admin():
    try:
        username, password, email = input_user()
        User.create(username=username, password=password, email=email, isadmin=True).save()
    except:
        app_log.error("The database table has not been created yet, you should first execute SpiderMan init")