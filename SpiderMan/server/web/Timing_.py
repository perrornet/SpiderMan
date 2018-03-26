# -*- coding:utf-8 -*-
import time

from tornado.log import app_log
from SpiderMan.utils.DataBase import MyManager
from SpiderMan.server.web.models import Timing, Host, get_datebase
from SpiderMan.Scrapyd_api.client import ScrapyApi

app = MyManager(get_datebase())


def scrapyd_object(host_info, ismodels=False, timeout=10):
    """get scrapy_spi object
        cache scrapy_api object. cache time : 60
    """
    if not host_info:
        return None
    if ismodels is True:
        return ScrapyApi(target="http://{}:{}".format(host_info.host, host_info.port), timeout=timeout)
    return ScrapyApi(target="http://{}:{}".format(host_info.host, host_info.port), timeout=timeout)


cache = {}
try:
    for i in Host.select():
        cache[i.id_] = scrapyd_object(i)
except:
    pass


# count = 1

async def timing():
    """A simple polling timing program
    """
    # global count

    if not cache:
        return

    timing_info = await app.get(Timing.select())
    if not timing_info:
        return
    for i in timing_info:
        if time.time() - i.last_time >= i.run_time:
            try:
                await cache[i.host_id].schedule(project=i.project_name, spider=i.spider_name)
                i.last_time = time.time()
                await app.update(i, only=[Timing.last_time])
                # count += 1
                # print(count)
                # app_log.info("runing timing task ok: {}".format(i.spider_name))
            except Exception as f:
                app_log.error(f)
