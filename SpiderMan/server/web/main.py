# -*- coding:utf-8 -*-
import os
import base64
import uuid

import tornado.web
import tornado.options
import tornado.ioloop
import tornado.httpserver
from tornado.log import app_log
from SpiderMan.hello import hello
from SpiderMan.model import SpiderManConf
from SpiderMan.server.web.Timing_ import timing
from SpiderMan.server.web.webSsh.handlers import (
    WSHandler, IndexHandler as WebSshIndexHandler,
)
from SpiderMan.server.web.webSsh.ioloop import IOLoop

from SpiderMan.server.web.views import (
    EditFileHandler, IndexHandler, LoginHandler,
    HostListHandler,SchedulHandler, TimingHtmlHandler, ProjectHandler,
)

from SpiderMan.server.web.api import (
    ListJobsHandler, ListProjectHandler, ListSpiderHandler,
    SpiderLogHandler, SpiderCancelHandler, RunSpiderHandler,
    DeleteProjectHandler, StartProjectHandler,
    FileCodeHandler, UpdateFileHandler, DeleteHostHandler,
    HostHomeHandler, ModifyConfHandler,
    StopSpiderHandler, SetTimingHandler, GetTimingHandler,
    HostSshHandler, LocationListProjectHandler, NewHostHandler,
    DeleteLocationProjectHandler, DeployProjectHandler,
    LocationListSpiderHandler, AuthHandler
)


def url_conf():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(BASE_DIR, 'templates')
    static_path = os.path.join(template_path, 'static')
    tornado.options.parse_command_line()
    settings = {
        "cookie_secret": base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
        "login_url": "/html/admin/login/",
        'gzip': True,
        'default_handler_class': IndexHandler,
    }

    views_urls = [
        (r"/ws", WSHandler),
        (r'^/html/admin/login/$', LoginHandler),
        (r'^/html/Host/host_list/$', HostListHandler),
        (r"^/html/Host/(\S+)/WebSshIndex/$", WebSshIndexHandler),
        (r"^/html/Host/(\S+)/spider/Schedul/$", SchedulHandler),
        (r"^/html/Host/(\S+)/spider/Timing/$", TimingHtmlHandler),
        (r"^/html/Project/(\S+)/edit_file/$", EditFileHandler),
        (r"^/html/project/$", ProjectHandler),
    ]

    apis_urls = [
        (r'^/api/admin/auth/$', AuthHandler),
        # 主机详情首页api
        (r'^/api/web/Host/$', HostHomeHandler),
        # 新建主机
        (r'^/api/web/Host/newHost/$', NewHostHandler),
        # 主机上所有的项目
        (r'^/api/web/Host/(\S+)/list_project/$', ListProjectHandler),
        # 主机ssh
        (r'^/api/web/Host/(\S+)/host_shh/$', HostSshHandler),
        # 删除主机
        (r'^/api/web/Host/(\S+)/delete_host/$', DeleteHostHandler),
        # 主机上正在运行的spider
        (r'^/api/web/Host/(\S+)/project/(\S+)/list_job/$', ListJobsHandler),
        # 主机上所有的spider
        (r'^/api/web/Host/(\S+)/project/(\S+)/list_spider/$', ListSpiderHandler),
        # 主机上指定项目中spider 的log
        (r'^/api/web/Host/(\S+)/project/(\S+)/spider_log/(\S+)/(\S+)/$', SpiderLogHandler),
        # 停止運行主机上的spider
        (r'^/api/web/Host/(\S+)/project/(\S+)/spider_cancel/(\S+)/$', SpiderCancelHandler),
        # 运行指定主机上项目中的spider
        (r'^/api/web/Host/(\S+)/project/(\S+)/run_spider/(\S+)/$', RunSpiderHandler),
        # 停止运行指定主机上项目的spider
        (r'^/api/web/Host/(\S+)/project/(\S+)/Stop_spider/(\S+)/$', StopSpiderHandler),
        # 删除指定主机上的指定项目
        (r'^/api/web/Host/(\S+)/project/(\S+)/delete_project/$', DeleteProjectHandler),
        # 修改主机信息
        (r'^/api/web/Host/(\S+)/modify_Conf/$', ModifyConfHandler),
        # 新建一个本地项目
        (r'^/api/web/Project/start_project/$', StartProjectHandler),
        # 删除一个本地项目
        (r'^/api/web/Project/delete_project/(\S+)/$', DeleteLocationProjectHandler),
        # 部署本地项目呆指定主机
        (r'^/api/web/Project/deploy_project/(\S+)/(\S+)/$', DeployProjectHandler),
        # 本地所有的项目
        (r'^/api/web/Project/list_project/$', LocationListProjectHandler),
        # 本地項目中所有的spider
        (r'^/api/web/Project/(\S+)/list_spider/$', LocationListSpiderHandler),
        # 暂时是log 展示
        (r'^/api/web/Project/(\S+)/file_code/(\S+)/$', FileCodeHandler),
        # 更新文件
        (r'^/api/web/Project/(\S+)/update_file/(\S+)/$', UpdateFileHandler),
        # # ssh
        # (r'^/api/web/Ssh/(\S+)/$', SshHandler),
        # 设置指定主机中指定项目的指定spider 定时任务
        (r'^/api/web/Host/(\S+)/Project/(\S+)/timing_spider/(\S+)/(\S+)/$', SetTimingHandler),

        # 获取指定主机中指定项目的指定spider 定时任务
        (r'^/api/web/Host/(\S+)/Project/(\S+)/get_timing_spider/(\S+)/$', GetTimingHandler),
    ]
    return tornado.web.Application(views_urls + apis_urls, static_path=static_path, template_path=template_path, debug=True, **settings)


def main(**kwargs):
    if not kwargs.get('dom'):
        kwargs['host'] = SpiderManConf.HOST
        kwargs['port'] = SpiderManConf.PORT
    else:
        kwargs['host'] = kwargs['dom'].split(':')[0]
        kwargs['port'] = kwargs['dom'].split(':')[1]
    app_log.error(hello.format(host=kwargs['host'], port=kwargs['port']))
    http_server = tornado.httpserver.HTTPServer(url_conf())
    http_server.listen(kwargs['port'], address=kwargs['host'])
    IOLoop.instance().start()
    tornado.ioloop.IOLoop.instance().start()
    tornado.ioloop.PeriodicCallback(timing, 5000).start()


if __name__ == '__main__':
    main()
