import os
import time
import urllib
import hashlib
from threading import Thread
from collections import defaultdict

import requests
import tornado.web
from tornado import escape
from tornado.escape import utf8
from scrapyd_api.exceptions import ScrapydResponseError

from SpiderMan.model import getIp, SpiderManConf
from SpiderMan.model.cache import cache
from SpiderMan.model.start_scrapy_project import StartScrapyProject
from SpiderMan.model.gen_scrapy_spider import GenSpider
from SpiderMan.model.scrapy_api import ScrapydAPI_, base_url
from SpiderMan.server.web.models import Host, Project, User, Timing
from SpiderMan.model.scrapy_project import delete_scrapy_project, build_egg


@cache(60)
def scrapyd_object(host_id, ismodels=False, timeout=10):
    """get scrapy_spi object
        cache scrapy_api object. cache time : 60
    """
    host_info = Host.getOne(Host.id_ == host_id)
    if not host_info:
        return None
    if ismodels is True:
        return ScrapydAPI_(base_url(host=host_info.host, port=host_info.port), timeout=timeout), host_info
    return ScrapydAPI_(base_url(host=host_info.host, port=host_info.port), timeout=timeout)


class BaseHandler(tornado.web.RequestHandler):
    def write(self, chunk, status_code=200):
        if self._finished:
            raise RuntimeError("Cannot write() after finish()")
        if isinstance(chunk, dict):
            chunk = escape.json_encode(chunk)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        chunk = utf8(chunk)
        self._write_buffer.append(chunk)
        self.set_status(status_code=status_code)

    def get_all_argument(self):
        data = {}
        for i in self.request.body.decode().split('&'):
            _, data[_] = i.split("=")
            data[_] = urllib.parse.unquote(data[_])
        return data

    def post(self, *args, **kwargs):
        self.write({"msg": "Server undefined post method!", "data": False})
        self.set_status(status_code=401)

    def put(self, *args, **kwargs):
        self.write({"msg": "Server undefined put method!", "data": False})
        self.set_status(status_code=401)

    def delete(self, *args, **kwargs):
        self.write({"msg": "Server undefined delete method!", "data": False})
        self.set_status(status_code=401)

    def get(self, *args, **kwargs):
        self.write({"msg": "Server undefined get method!", "data": False})
        self.set_status(status_code=401)

    def options(self, *args, **kwargs):
        self.write({"msg": "Server undefined options method!", "data": False})
        self.set_status(status_code=401)

    def head(self, *args, **kwargs):
        self.write({"msg": "Server undefined head method!", "data": False})
        self.set_status(status_code=401)

    def patch(self, *args, **kwargs):
        self.write({"msg": "Server undefined patch method!", "data": False})
        self.set_status(status_code=401)

    def data_received(self, chunk):
        pass

    def send_error(self, status_code=500, **kwargs):
        self.write({"msg": "server error!"})
        self.set_status(status_code=500)

    def get_current_user(self):
        return self.get_secure_cookie('user')

    def has_password(self, passwrod):
        """对密码进行加密"""
        return hashlib.md5(passwrod.encode()).hexdigest()


class SshHandler(BaseHandler):
    """get server username and password

    :GET param host_id: server id
    """

    def get(self, host_id):
        host_info = Host.getOne(Host.id_ == host_id)
        if not host_info:
            self.write({"data": False, "msg": "server error"}, status_code=500)
            return
        if not host_info.host_ssh_name or not host_info.host_ssh_password:
            self.write({
                "data": False, "msg": "host ssh name: {}, password: {}".format(
                    host_info.host_ssh_name, host_info.host_ssh_password
                )
            }, status_code=404)
            return
        self.write({"data": {
            'host': getIp(host_info.host),
            'port': 22,
            'username': host_info.host_ssh_name,
            'secret': host_info.host_ssh_password,
            'name': host_info.name}, "msg": ""})


class ListJobsHandler(BaseHandler):
    """get server project runing spider

    :GET param host_id: server id
    :GET param project_name:  project name
    """

    def get(self, host_id, project_name):
        scrapyd = scrapyd_object(host_id, timeout=1)
        try:
            self.write({"data": scrapyd.list_jobs(project_name), "msg": ""})
        except:
            self.write({"msg": "spider host error!", "data": False}, status_code=500)


class SpiderLogHandler(BaseHandler):
    """get spider log file

    :GET param host_id: server id
    :GET param project_name: project name
    :GET param spider_name:  spider name
    :GET param spider_id:  scrapyd spider id
    """

    def get(self, host_id, project_name, spider_name, spider_id):
        scrapyd, host_info = scrapyd_object(host_id=host_id, ismodels=True)
        try:

            self.render(
                'file.html', id=1,
                code=scrapyd.spider_log(project_name=project_name, spider_name=spider_name,
                                        spider_id=spider_id).decode()
            )
        except:
            self.render('file.html', code='', id=0)


class RunSpiderHandler(BaseHandler):
    """runing apponit server spider

    :GET param host_id: server id
    :GET param project_name: project name
    :GET param spider_name: spider name
    """

    def get(self, host_id, project_name, spider_name):
        scrapyd = scrapyd_object(host_id=host_id, timeout=0.1)
        try:
            scrapyd.schedule(project=project_name, spider=spider_name)
            self.write({"data": True, "msg": ""})
        except ScrapydResponseError:
            self.write({"data": False, "msg": "server error"}, status_code=500)


class ListSpiderHandler(BaseHandler):
    """get server all spider

    :GET param host_id: server id
    :GET param project_name: project name
    """

    def get(self, host_id, project_name):

        scrapyd = scrapyd_object(host_id, timeout=1)
        try:
            self.write({"data": scrapyd.list_spiders(project_name), "msg": ""})
        except:
            self.write({"data": False, "msg": "server error"}, status_code=500)


class ListProjectHandler(BaseHandler):
    """get server all project

    :GET param host_id: server id
    """

    def get(self, host_id):

        scrapyd = scrapyd_object(host_id, timeout=1)
        try:
            self.write({"project": scrapyd.list_projects()})
        except :
            self.write({"msg": "scrapyd server error", "data": False}, status_code=500)
            return


class StartProjectHandler(BaseHandler):
    """create scrapy project

    :post_param project_name: scrapy priject name
    :post_param spdier_name: scrapy spider name
    :post_param project_description: scrapy project description
    :post_param scrapy_start_url: scrapy spider start url
    :post_param scrapyd_model: scrapy create spider model
    """

    def post(self):
        project_data = self.get_all_argument()
        project_info = Project.getOne(Project.project_name == project_data['project_name'])
        if project_info:
            self.write({"data": False, "msg": "project name exist"}, status_code=404)
            return
        Thread()
        isrun = StartScrapyProject().run(project_name=project_data['project_name'], project_dir=SpiderManConf.SPIDER_MAN_SCRAPY_FILE_PATH)
        if not isrun:
            self.write({"data": False,
                        "msg": "project name sxist.see {} dir".format(SpiderManConf.SPIDER_MAN_SCRAPY_FILE_PATH)},
                       status_code=500)
            return
        project_data.update({
            "domain": project_data.get("scrapy_start_url", 'example.com'),
            'project_path': SpiderManConf.SPIDER_MAN_SCRAPY_FILE_PATH,
            "template": project_data.get('scrapyd_model', 'basic')
        })
        isrun = GenSpider().run(**project_data)
        if isrun is False:
            self.write({"data": False, "msg": "build project spider error"}, status_code=500)
            return
        self.write({"data": {"project_name": project_data['project_name']}, "msg": ""})
        Project.create(
            create_time=time.time(), project_path=SpiderManConf.SPIDER_MAN_SCRAPY_FILE_PATH,
            project_name=project_data['project_name'], description=project_data.get('description', ''),
            update_time=time.time(), project_version=1
        ).save()


class SpiderCancelHandler(BaseHandler):
    """cancel runing spider job

    :GET param host_id: server id
    :GET param project_name: project name
    :GET param spider_id: runing scrapyd spider id
    """

    def get(self, host_id, project_name, spider_id):
        scrapyd = scrapyd_object(host_id=host_id, timeout=0.1)
        try:
            scrapyd.cancel(project=project_name, job=spider_id)
            self.write({"data": True, "msg": ""})
        except ScrapydResponseError:
            self.write({"data": False, "msg": "server error"}, status_code=500)


class DeleteProjectHandler(BaseHandler):
    """delete server apponit project
    :GET param host_id: server id
    :GET param project_name: project name
    """

    def delete(self, host_id, project_name):
        scrapyd = scrapyd_object(host_id=host_id, timeout=0.1)
        try:
            scrapyd.delete_project(project=project_name)
            Timing.delete().where(Timing.host_id == host_id, Timing.project_name == project_name).execute()
            Project.update(host_id=None).where(Project.project_name == project_name, Project.host_id == host_id).execute()
        except ScrapydResponseError:
            self.write({"data": False, "msg": "server error!"}, status_code=404)
            return []
        self.write({"data": True, "msg": ""})


class FileCodeHandler(BaseHandler):
    """get apponit file content

    :GET param project_id: local project id
    :GET param file_name: project file name
    """

    def get(self, project_id, file_name):
        project_info = Project.getOne(Project.id_ == project_id)
        if not project_info:
            self.write({"data": False, "msg": ""}, status_code=404)
            return
        file_path = os.path.join(project_info.project_path, project_info.project_name, 'spiders', file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            self.write({"data": f.read(), "msg": ""})


class UpdateFileHandler(BaseHandler):
    """ update apponit file content

    :POST param project_id: local project id
    :POST param file_name: file name
    """

    def post(self, project_id, file_name):
        project_info = Project.getOne(Project.id_ == project_id)
        if not project_info:
            self.write({"data": False, "msg": ""}, status_code=404)
            return
        try:
            file_path = os.path.join(project_info.project_path, project_info.project_name, 'spiders', file_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.get_argument('code'))
                self.write({"data": True, "msg": ""})
        except Exception as f:
            self.write({"data": False, "msg": "{}".format(f)}, status_code=500)
            return


class DeleteHostHandler(BaseHandler):
    """ delete apponit server

    :DELETE param host_id: server id
    """

    def delete(self, host_id):
        try:
            Host.delete().where(Host.id_ == host_id).execute()
            Timing.delete().where(Timing.host_id == host_id).execute()
            self.write({"data": True, "msg": ""})
        except:
            self.write({"data": False, "msg": ""}, status_code=500)


class HostHomeHandler(BaseHandler):
    """get server list
    """
    def get(self):
        data = []
        try:
            for host_info in Host.select():
                data.append({
                    'id': host_info.id_,
                    'host': host_info.host,
                    'port': host_info.port,
                    'name': host_info.name,
                    'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(host_info.create_time)),
                    'is_run': host_info.is_run
                })
            self.write({"data": data, "msg": ""})
        except:
            self.write({"data": False, "msg": "server error!"}, status_code=500)


class AuthHandler(BaseHandler):
    """login Verification
    """
    def post(self):
        username = self.get_argument("username")
        password = self.has_password(self.get_argument("password"))
        next = self.get_argument('next', '/index')
        if not username or not password:
            self.render('login.html', next=next, msg="")
            return []
        is_login = User.getOne(User.username == username, User.password == password)
        if is_login is not None:
            self.set_secure_cookie("user", "admin")
            self.redirect(next, permanent=True)
            return []
        self.render('login.html', next=next, msg="賬號密碼錯誤！")


class ModifyConfHandler(BaseHandler):
    """update server config
    """
    def is_true(self, parsm):
        return parsm == '0'

    def post(self, host_id):
        host_info = Host.getOne(Host.id_ == host_id)
        is_run = host_info.is_run
        if not is_run:
            try:
                requests.get("http://{}:{}".format(self.get_argument('host'), self.get_argument('port')), timeout=0.1)
                is_run = True
            except Exception as f:
                print(f)
        up_item = {
            'host': self.get_argument('host'), 'name': self.get_argument('name'),
            'scrapyd_name': self.get_argument('scrapyd_name'),
            'scrapyd_password': self.get_argument('scrapyd_password'),
            'host_ssh_name': self.get_argument('host_ssh_name'),
            'host_ssh_password': self.get_argument('host_ssh_password'),
            'port': self.get_argument('port'), 'is_run': is_run
        }
        try:
            Host.update(**up_item).where(Host.id_ == host_id).execute()
        except Exception as f:
            self.write({"data": False, "msg": '{}'.format(f)}, status_code=404)
            return
        return self.write({"data": True, "msg": ''})

    def get(self, host_id):

        try:
            host_info = Host.getOne(Host.id_ == host_id)
            self.write({"data": {
                'host': host_info.host, 'name': host_info.name,
                'scrapyd_name': host_info.scrapyd_name, 'scrapyd_password': host_info.scrapyd_password,
                'host_ssh_name': host_info.host_ssh_name, 'host_ssh_password': host_info.host_ssh_password,
                'port': host_info.port
            }, "msg": ""})
        except:
            self.write({"data": False, "msg": "host id not find"}, status_code=404)


class StopSpiderHandler(BaseHandler):
    """stop runing spider
    """
    def get(self, host_id, project_name, spider_id):
        try:
            scrapyd = scrapyd_object(host_id=host_id)
            scrapyd.cancel(project=project_name, job=spider_id)
            self.write({"data": True, "msg": "server error"})
        except:
            self.write({"data": False, "msg": "server error"})


class SetTimingHandler(BaseHandler):
    """set timing task
    """
    def post(self, host_id, project_name, spider_name, _time):
        try:
            timing_info = Timing.getOne(Timing.host_id == host_id, Timing.project_name == project_name,
                                        Timing.spider_name == spider_name)
            if not timing_info:
                # 新建
                Timing.create(
                    host_id=host_id,
                    project_name=project_name,
                    spider_name=spider_name,
                    last_time=time.time(),
                    run_time=_time,
                ).save()
            else:
                # 更新
                Timing.update(
                    last_time=time.time(),
                    run_time=_time
                ).execute()
            self.write({"data": True, "msg": ""})

        except Exception as f:
            self.write({"data": False, "msg": str(f)})
            self.set_status(status_code=500)


class GetTimingHandler(BaseHandler):
    """get task timing
    """
    def get(self, host_id, project_name, spider_name):
        timing_info = Timing.getOne(Timing.host_id == host_id, Timing.project_name == project_name,
                                    Timing.spider_name == spider_name)
        if not timing_info:
            self.write({"data": False, "msg": ""})
        else:
            self.write({
                "data": {
                    "host_id": timing_info.host_id,
                    "project_name": timing_info.project_name,
                    "spider_name": timing_info.spider_name,
                    "last_time": timing_info.last_time,
                    "run_time": timing_info.run_time
                },
                "msg": ""
            })


class HostSshHandler(BaseHandler):
    """get server ssh info
    """
    def get(self, host_id):
        host_info = Host.getOne(Host.id_ == host_id)
        if not host_info:
            self.write({"data": False, "msg": "not find host!"})
            self.set_status(status_code=404)
            return
        try:
            self.write({
                "data": {
                    "host": getIp(host_info.host), "port": host_info.port,
                    "username": host_info.host_ssh_name, "secret": host_info.host_ssh_password
                }, "msg": ""})
        except:
            self.write(
                {"data": False, "msg": "host error: {host}:{port}".format(host=host_info.host, port=host_info.port)})
            self.set_status(status_code=404)


class LocationListProjectHandler(BaseHandler):
    """get local project list
    """
    def get(self, *args, **kwargs):
        data = []
        for project_info in Project.select():
            data.append({
                "description": project_info.description,
                "update_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(project_info.update_time)),
                "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(project_info.create_time)),
                "project_name": project_info.project_name,
                "project_version": project_info.project_version,
                "id": project_info.id_, "host_id": project_info.host_id,
            })
        self.write({"data": data or False, "msg": ""})


class LocationListSpiderHandler(BaseHandler):
    """get local list spider
    """
    def get(self, project_id):
        project_info = Project.getOne(Project.id_ == project_id)
        if not project_info:
            self.write({"data": False, "msg": "not find project!"})
            self.set_status(status_code=404)
            return
        data = [i for i in os.listdir(os.path.join(project_info.project_path, project_info.project_name, 'spiders')) if
                '__init__' not in i and '.py' in i]
        self.write({"data": data, "msg": ""})


class NewHostHandler(BaseHandler):
    """new link scrapyd server
    """
    def post(self, *args, **kwargs):
        try:
            isrun = True
            try:
                requests.get("http://{}:{}".format(self.get_argument('host_id'), self.get_argument('host_port')), timeout=0.1)
            except:
                isrun = False
            host = self.get_argument('host_id')
            if 'http' in host:
                host = host.split('http://')[-1]
            Host.create(
                host=self.get_argument('host_id'), name=self.get_argument('host_name'),
                scrapyd_name=self.get_argument('scrapy_name', ''),
                scrapyd_password=self.get_argument('scrapy_password', ''),
                host_ssh_name=self.get_argument('ssh_name', ''), host_ssh_password=self.get_argument('ssh_password'),
                port=self.get_argument('host_port'), create_time=time.time(), is_run=isrun
            ).save()
            self.write({"data": True, "msg": ""})
        except Exception as f:
            self.write({"data": False, "msg": "{}".format(f)})
            self.set_status(status_code=500)


class DeleteLocationProjectHandler(BaseHandler):
    """delect local project
    """
    def delete(self, project_name):
        project_info = Project.getOne(Project.project_name == project_name)
        if not project_info:
            self.write({"data": False, "msg": "{} project not sxist!".format(project_name)})
            self.set_status(status_code=404)
            return
        try:

            if not delete_scrapy_project(project_info.project_path, project_name):
                self.write({"data": False, "msg": "server error"})
                self.set_status(status_code=500)
                return
            else:
                Project.delete().where(Project.id_ == project_info.id_).execute()
                self.write({"data": True, "msg": ""})
        except Exception as f:
            self.write({"data": False, "msg": "{}".format(f)})
            self.set_status(status_code=500)
            return


class DeployProjectHandler(BaseHandler):
    """deploy local project to scrapy server
    """
    def post(self, host_id, project_id):
        print(project_id)
        project_info = Project.getOne(Project.id_ == project_id)
        if not project_info or not os.path.exists(project_info.project_path):
            self.write({"data": False, "msg": "not find project name"})
            self.set_status(status_code=404)
            return

        # build egg
        egg_file_path = build_egg(
            project_path=project_info.project_path,
            name=project_info.project_name,
            version=project_info.project_version,
            SCRAPY_SETUP_CODE=SpiderManConf.SCRAPY_SETUP_CODE
        )

        # scrapyd deploy
        scrapyd = scrapyd_object(host_id=host_id)
        try:
            scrapyd.add_version(
                project=project_info.project_name, egg=open(egg_file_path, 'rb').read(),
                version=project_info.project_version
            )
            Project.update(host_id=host_id).where(Project.id_ == project_id).execute()
            self.write({"data": True, "msg": ""})
        except Exception as f:
            self.write({"data": False, "msg": str(f)})
            self.set_status(status_code=500)
