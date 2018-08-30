# -*- coding:utf-8 -*-
import hashlib

import tornado.web
from SpiderMan.utils.model_to_dict import ModelsToDict as models_to_dict
from SpiderMan.server.web.models import Host


class BaseHandler(tornado.web.RequestHandler):
    def requests(self, method, url, **kwargs):
        return requests.Request(method, url, **kwargs)

    def has_password(self, passwrod):
        """对密码进行加密"""
        return hashlib.md5(passwrod.encode()).hexdigest()

    def data_received(self, chunk):
        pass

    def send_error(self, status_code=500, **kwargs):
        self.render('404.html')

    def write_error(self, status_code, **kwargs):
        self.render('404.html')

    def get_current_user(self):
        return self.get_secure_cookie('user')


class ErrorHandler(BaseHandler):
    pass


class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render('index.html')


class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        next = self.get_argument('next', '/index')
        self.render('login.html', next=next, msg="", message="")


class HostListHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, *args, **kwargs):
        query = await self.application.objects.get(Host.select())
        self.render('host_list.html', item=models_to_dict(query).data)


class DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        _id = self.get_argument('id', 0)
        Host.delete().where(Host.id_ == _id).execute()
        self.write(self.put_jsonp({"msg": "OK"}))


class SchedulHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, host_id):
        self.render('schedul.html')


class TimingHtmlHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render('timing.html')


class ReadFileHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render('file.html')


class ProjectHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render('project.html')


class EditFileHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, project_id):
        self.render('edit_scrapy_file.html')
