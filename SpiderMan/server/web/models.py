# -*- coding:utf-8 -*-
import os

from peewee import *
import peewee_async
from SpiderMan.utils import SpiderManConf


def get_datebase(dbname='SpiderMan'):
    return peewee_async.PooledMySQLDatabase(dbname, host=SpiderManConf.MYSQLHOST, port=3306,
                                            user=SpiderManConf.MYSQLUSER, password=SpiderManConf.MYSQLPASSWORD,
                                            charset='utf8')


class BaseModel(Model):
    @classmethod
    def getOne(cls, *query, **kwargs):
        try:
            return cls.get(*query, **kwargs)
        except:
            return None

    class Meta:
        database = get_datebase()


class User(BaseModel):
    id_ = PrimaryKeyField(db_column="id")
    username = CharField(verbose_name="用户账号")
    password = CharField(verbose_name="用户密码", max_length=64, null=False)
    isadmin = BooleanField(verbose_name="是否拥有管理员权限")
    email = CharField(verbose_name="用户邮箱", max_length=120)

    class meta:
        order_by = 'id'
        db_table = 'user'


class Project(BaseModel):
    id_ = PrimaryKeyField(db_column="id")
    host_id = IntegerField(verbose_name="主机id", null=True)
    project_name = CharField(verbose_name="项目名称", max_length=256)
    description = CharField(verbose_name="项目描述", max_length=256, null=True)
    create_time = IntegerField(verbose_name="项目创建时间")
    update_time = IntegerField(verbose_name="项目最近一次更新时间")
    project_path = CharField(verbose_name="项目目录", max_length=256)
    project_version = CharField(verbose_name="项目版本号", max_length=256, null=True)

    class meta:
        order_by = 'id'
        db_table = 'project'


class Timing(BaseModel):
    id_ = PrimaryKeyField(db_column="id")
    host_id = IntegerField(verbose_name="主机id", null=True)
    project_name = CharField(verbose_name="项目名称", null=True)
    spider_name = CharField(verbose_name="蜘蛛名称", max_length=256)
    last_time = IntegerField(verbose_name="上一次运行时间")
    run_time = IntegerField(verbose_name="运行间隔")

    class meta:
        order_by = 'id'
        db_table = 'timing'


class Host(BaseModel):
    id_ = PrimaryKeyField(db_column="id")
    host = CharField(null=False, verbose_name="主机ip", max_length=24)
    name = CharField(null=False, verbose_name="主机別稱", max_length=128)
    scrapyd_name = CharField(null=True, verbose_name="主机scrapyd名称", max_length=128)
    scrapyd_password = CharField(null=True, verbose_name="主机scrapyd密码", max_length=128)
    port = IntegerField(null=False, verbose_name="主机端口")
    create_time = IntegerField(null=False, verbose_name="创建时间")
    is_run = BooleanField(verbose_name="是否運行中")

    class meta:
        order_by = 'id'
        db_table = 'host'
