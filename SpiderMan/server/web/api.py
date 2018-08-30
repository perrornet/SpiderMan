# -*- coding: utf-8 -*-
"""SpiderMan 的 api
"""
import os
import time
from tornado import escape
from tornado.log import app_log

from SpiderMan.utils import SpiderManConf
from SpiderMan.utils.cache import cache
from SpiderMan.utils.model_to_dict import ModelsToDict
from SpiderMan.utils.tornado_model import BaseHandler
from SpiderMan.utils.start_scrapy_project import StartScrapyProject
from SpiderMan.utils.gen_scrapy_spider import GenSpider
from SpiderMan.Scrapyd_api.client import ScrapyApi
from SpiderMan.server.web.models import Timing
from SpiderMan.server.web.models import User
from SpiderMan.server.web.models import Project
from SpiderMan.server.web.models import Host
from SpiderMan.utils.scrapy_project import build_egg
from SpiderMan.utils.scrapy_project import delete_scrapy_project
from SpiderMan.utils.DataBase import MyManager
from SpiderMan.server.web.models import get_datebase

app = MyManager(get_datebase())

@cache(60)
def scrapyd_object(host_info, ismodels=False, timeout=10):
    """get scrapy_spi object
        cache scrapy_api object. cache time : 60
    """
    if not host_info:
        return None
    if ismodels is True:
        return ScrapyApi(target="http://{}:{}".format(host_info.host, host_info.port), timeout=timeout), host_info
    return ScrapyApi(target="http://{}:{}".format(host_info.host, host_info.port), timeout=timeout)


class ListJobsHandler(BaseHandler):
    """get server project runing spider

    :GET param host_id: server id
    :GET param project_name:  project name
    """

    async def get(self, host_id, project_name):
        host_info = await self.application.objects.get(Host, id_=host_id)
        scrapyd = scrapyd_object(host_info, timeout=1)
        response = await scrapyd.list_jobs(project=project_name)
        self.write({"data": escape.json_decode(response.body)})


class SpiderLogHandler(BaseHandler):
    """get spider log file

    :GET param host_id: server id
    :GET param project_name: project name
    :GET param spider_name:  spider name
    :GET param spider_id:  scrapyd spider id
    """

    async def get(self, host_id, project_name, spider_name, spider_id):
        host_info = await self.application.objects.get(Host, id_=host_id)
        scrapyd = scrapyd_object(host_info, timeout=1)
        try:
            code = await scrapyd.spider_log(
                project_name=project_name, spider_name=spider_name, spider_id=spider_id)
            self.render('file.html', id=1, code=code.body)
        except Exception as f:
            app_log.error(str(f))
            self.render('404.html')


class RunSpiderHandler(BaseHandler):
    """runing apponit server spider

    :GET param host_id: server id
    :GET param project_name: project name
    :GET param spider_name: spider name
    """

    async def get(self, host_id, project_name, spider_name):
        host_info = await self.application.objects.get(Host, id_=host_id)
        scrapyd = scrapyd_object(host_info, timeout=1)
        await scrapyd.schedule(project=project_name, spider=spider_name)
        self.write({"data": True})


class ListSpiderHandler(BaseHandler):
    """get server all spider

    :GET param host_id: server id
    :GET param project_name: project name
    """

    async def get(self, host_id, project_name):
        host_info = await self.application.objects.get(Host, id_=host_id)
        scrapyd = scrapyd_object(host_info, timeout=1)
        response = await scrapyd.list_spiders(project_name)
        self.write({"data": escape.json_decode(response.body)})


class ListProjectHandler(BaseHandler):
    """get server all project

    :GET param host_id: server id
    """

    async def get(self, host_id):
        host_info = await self.application.objects.get(Host, id_=host_id)
        scrapyd = scrapyd_object(host_info, timeout=1)
        response = await scrapyd.list_projects()
        self.write({"data": escape.json_decode(response.body)})


class StartProjectHandler(BaseHandler):
    """create scrapy project

    :post_param project_name: scrapy priject name
    :post_param spdier_name: scrapy spider name
    :post_param project_description: scrapy project description
    :post_param scrapy_start_url: scrapy spider start url
    :post_param scrapyd_model: scrapy create spider utils
    """

    async def post(self):
        project_data = self.get_all_argument()
        project_info = await self.application.objects.get(Project, project_name=project_data['project_name'])
        if project_info is not None:
            self.write({"data": False, "msg": "project name exist"}, status_code=404)
            return
        isrun = StartScrapyProject().run(
            project_name=project_data['project_name'],
            project_dir=SpiderManConf.SPIDER_MAN_SCRAPY_FILE_PATH)
        if not isrun:
            self.write({"data": False, "msg": "project name sxist.see {} dir".format(
                SpiderManConf.SPIDER_MAN_SCRAPY_FILE_PATH)}, status_code=500)
            return
        GenSpider().run(**{
            'template': project_data.get('scrapyd_model', 'basic'),
            'spider_name': project_data["spider_name"],
            'project_name': project_data["project_name"],
            'domain': project_data.get("scrapy_start_url", 'example.com'),
            'path': SpiderManConf.SPIDER_MAN_SCRAPY_FILE_PATH
        })

        if isrun is False:
            self.write({"data": False,
                        "msg": "build project spider error"},
                       status_code=500)
            return
        self.write({"data": {"project_name": project_data['project_name']}})
        await self.application.objects.create(
            Project, create_time=time.time(),
            project_path=SpiderManConf.SPIDER_MAN_SCRAPY_FILE_PATH,
            project_name=project_data['project_name'],
            description=project_data.get('description', ''),
            update_time=time.time(),
            project_version=1)


class SpiderCancelHandler(BaseHandler):
    """cancel runing spider job

    :GET param host_id: server id
    :GET param project_name: project name
    :GET param spider_id: runing scrapyd spider id
    """

    async def get(self, host_id, project_name, spider_id):
        host_info = await self.application.objects.get(Host, id_=host_id)
        
        scrapyd = scrapyd_object(host_info, timeout=1)
        await scrapyd.cancel(project=project_name, job=spider_id)
        self.write({"data": True})


class DeleteProjectHandler(BaseHandler):
    """delete server apponit project
    :GET param host_id: server id
    :GET param project_name: project name
    """

    async def delete(self, host_id, project_name):
        host_info = await self.application.objects.get(Host, id_=host_id)
        scrapyd = scrapyd_object(host_info, timeout=1)
        response = await scrapyd.delete_project(project=project_name)
        timein = await self.application.objects.get(Timing, project_name=project_name, host_id=host_id)
        if timein is not None:
            await self.application.objects.delete(timein)
        project_info = await self.application.objects.get(Project, host_id=host_id, project_name=project_name)
        project_info.host_id = None
        await self.application.objects.update(project_info, only=[Project.host_id])
        self.write({"data": True})


class FileCodeHandler(BaseHandler):
    """get apponit file content

    :GET param project_id: local project id
    :GET param file_name: project file name
    """

    async def get(self, project_id, file_name):
        project_info = await self.application.objects.get(Project, id_=project_id)
        if project_info is None:
            self.write({"data": False, "msg": "not find project"}, status_code=404)
            return
        file_path = os.path.join(
            project_info.project_path, project_info.project_name, 'spiders', file_name
        )
        with open(file_path, 'r', encoding='utf-8') as f:
            self.write({"data": f.read()})


class UpdateFileHandler(BaseHandler):
    """ update apponit file content

    :POST param project_id: local project id
    :POST param file_name: file name
    """

    async def post(self, project_id, file_name):
        project_info = await self.application.objects.get(Project, id_=project_id)
        if project_info is None:
            self.write({"data": False, "msg": "project not find"}, status_code=404)
            return
        file_path = os.path.join(
            project_info.project_path, project_info.project_name, 'spiders', file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.get_argument('code'))
            self.write({"data": True})


class DeleteHostHandler(BaseHandler):
    """ delete apponit server

    :DELETE param host_id: server id
    """

    async def delete(self, host_id):
        await self.application.objects.delete(Host.getOne(Host.id_ == host_id))
        await self.application.objects.delete(Timing.getOne(Timing.host_id == host_id))
        self.write({"data": True})


class HostHomeHandler(BaseHandler):
    """get server list
    """

    async def get(self):
        host_info = await self.application.objects.get(Host.select())
        if not host_info:
            self.write({"data": False, "msg": "server error!"}, status_code=500)
            return []
        data = ModelsToDict(
            data=host_info, field_name={'id_': 'id'},
            shield_field=[Host.scrapyd_password],
            field_handle={Host.create_time: self.time2time})
        self.write({"data": data})


class AuthHandler(BaseHandler):
    """login Verification
    """

    async def post(self):
        username = self.get_argument("username")
        password = self.has_password(self.get_argument("password"))
        next = self.get_argument('next', '/index')
        if not username or not password:
            self.render('login.html', next=next, msg="")
            return []
        try:
            is_login = await self.application.objects.get(User, username=username, password=password)
            if is_login:
                self.set_secure_cookie("user", "admin")
                self.redirect(next, permanent=True)
                return []
        except Exception as e:
            app_log.error(e)
            self.render('login.html', next=next, msg="server error", message="")
            return
        self.render('login.html', next=next, msg="账号密码错误！", message="")



class ModifyConfHandler(BaseHandler):
    """update server config
    """

    async def post(self, host_id):
        host_info = await self.application.objects.get(Host, id_=host_id)
        if host_info is None:
            self.write({"data": False, "msg": "not find host"}, 404)
            return
        host = self.get_argument('host')
        if 'http' in host:
            host = host.split('http://')[-1]
        isrun = await self.ping(url='http://{}:{}'.format(host, self.get_argument('port')))
        host_info.host = host
        host_info.name = self.get_argument('name')
        host_info.scrapyd_name = self.get_argument('scrapyd_name')
        host_info.scrapyd_password = self.get_argument('scrapyd_password')
        host_info.port = self.get_argument('port')
        host_info.is_run = isrun
        await self.application.objects.update(host_info, only=[
            Host.host, Host.name, Host.scrapyd_name,
            Host.scrapyd_password,  Host.port, Host.is_run
        ])
        self.write({"data": True})

    async def get(self, host_id):
        host_info = await self.application.objects.get(Host, id_=host_id)
        if host_info is None:
            self.write({"data": False, "msg": "not find host"}, 404)
            return
        self.write({"data": ModelsToDict(
            data=host_info)
        })


class StopSpiderHandler(BaseHandler):
    """stop runing spider
    """

    async def get(self, host_id, project_name, spider_id):
        host_info = await self.application.objects.get(Host, id_=host_id)
        scrapyd = scrapyd_object(host_info, timeout=1)
        await scrapyd.cancel(project=project_name, job=spider_id)
        self.write({"data": True})



class SetTimingHandler(BaseHandler):
    """set timing task
    """

    async def post(self, host_id, project_name, spider_name, _time):
        timing_info = await self.application.objects.get(
            Timing, host_id=host_id,
            project_name=project_name, spider_name=spider_name)
        if timing_info is None:
            # 新建
            await self.application.objects.create(
                Timing,
                host_id=host_id, project_name=project_name,
                spider_name=spider_name, last_time=time.time(),
                run_time=_time)
        else:
            # 更新
            timing_info.last_time = time.time()
            timing_info.run_time = _time
            await self.application.objects.update(
                timing_info, only=[Timing.last_time, Timing.run_time])
        self.write({"data": True})


class GetTimingHandler(BaseHandler):
    """get task timing
    """

    async def get(self, host_id, project_name, spider_name):
        timing_info = await self.application.objects.get(
                Timing, host_id=host_id, project_name=project_name, spider_name=spider_name)
        if timing_info is None:
            self.write({"data": False})
            return
        out_object = ModelsToDict(
            data=timing_info, field_name={Timing.id_: "id"})
        self.write({"data": out_object})


class LocationListProjectHandler(BaseHandler):
    """get local project list
    """

    async def get(self, *args, **kwargs):
        project_info = await self.application.objects.get(Project.select())
        out_object = ModelsToDict(
            data=project_info, field_name={Project.id_: "id"},
            field_handle={Project.create_time: self.time2time, Project.update_time: self.time2time})
        self.write({"data": out_object or False,
                    "msg": "local not find project"})


class LocationListSpiderHandler(BaseHandler):
    """get local list spider
    """

    async def get(self, project_id):
        project_info = await self.application.objects.get(Project, id_=project_id)
        if project_info is None:
            self.write({"data": False, "msg": "not find project!"}, 404)
            return
        data = [
            i for i in os.listdir(
                os.path.join(
                    project_info.project_path,
                    project_info.project_name,
                    'spiders')) if '__init__' not in i and '.py' in i]
        self.write({"data": data})


class NewHostHandler(BaseHandler):
    """new link scrapyd server
    """

    async def post(self, *args, **kwargs):
        host = self.get_argument('host_id')
        if 'http' in host:
            host = host.split('http://')[-1]
        isrun = await self.ping(url='http://{}:{}'.format(host, self.get_argument('host_port')))
        inst = await self.application.objects.create(
            Host, host=host, name=self.get_argument('host_name'),
            scrapyd_name=self.get_argument('scrapy_name', ''),
            scrapyd_password=self.get_argument('scrapy_password', ''),
            port=self.get_argument('host_port'),
            create_time=time.time(), is_run=isrun)
        if inst is None:
            self.write({"data": False, "msg": "dataBase error!"}, status_code=404)
            return
        self.write({"data": True})


class DeleteLocationProjectHandler(BaseHandler):
    """delect local project
    """

    async def delete(self, project_name):
        project_info = await self.application.objects.get(Project, project_name=project_name)
        if project_info is None:
            self.write(
                {"data": False, "msg": "{} project not sxist!".format(project_name)},
                status_code=404)
            return
        if not delete_scrapy_project(project_info.project_path, project_name):
            self.write({"data": False, "msg": "server error"}, status_code=500)
            return
        await self.application.objects.delete(project_info)
        self.write({"data": True})


class DeployProjectHandler(BaseHandler):
    """deploy local project to scrapy server
    """

    async def post(self, host_id, project_id):
        project_info = await self.application.objects.get(Project, id_=project_id)
        if project_info is None or not os.path.exists(project_info.project_path):
            self.write({"data": False, "msg": "not find project name"}, status_code=404)
            return
        # build egg
        egg_file_path = build_egg(
            project_path=project_info.project_path,
            name=project_info.project_name,
            version=project_info.project_version,
            SCRAPY_SETUP_CODE=SpiderManConf.SCRAPY_SETUP_CODE
        )
        # scrapyd deploy
        host_info = await self.application.objects.get(Host, id_=host_id)
        scrapyd = scrapyd_object(host_info, timeout=1)
        response = await scrapyd.add_version(
            project=project_info.project_name,
            egg=open(egg_file_path, 'rb').read(), version=project_info.project_version)
        if response.code // 100 != 2:
            self.write({"data": False, "msg": "scrapyd server error"}, status_code=500)
        project_info.host_id = host_id
        await self.application.objects.update(project_info, only=[Project.host_id])
        print(response.body.decode())
        self.write({"data": True})


class MonitorHostHandler(BaseHandler):
    """监控主机是否正常, 监控爬虫log 是否出错
    """
    def get(self, *args, **kwargs):
        pass


