# -*- coding:utf-8 -*-
import time

from tornado.log import app_log

from SpiderMan.server.web.models import Timing, Host
from SpiderMan.model.scrapy_api import ScrapydAPI_, base_url


def scrapyd_object(host_id, ismodels=False):
    host_info = Host.getOne(Host.id_ == host_id)
    if not host_info:
        return None
    if ismodels is True:
        return ScrapydAPI_(base_url(host=host_info.host, port=host_info.port)), host_info
    return ScrapydAPI_(base_url(host=host_info.host, port=host_info.port))


cache = {}
try:
    for i in Host.select():
        cache[i.id] = scrapyd_object(host_id=i.id)
except:
    pass


def timing():
    """A simple polling timing program
    """
    if not cache:
        return
    for i in Timing.select():
        if time.time() - i.last_time >= i.run_time:
            try:
                cache[i.host_id].schedule(project=i.project_name, spider=i.spider_name)
                Timing.update(last_time=time.time()).where(Timing.id_ == i.host_id)
            except AttributeError:
                Timing.delete().where(Timing.id_ == i.id_).execute()
            except KeyError:
                Timing.delete().where(Timing.host_id == i.host_id).execute()
            except Exception as f:
                app_log.error(f)
