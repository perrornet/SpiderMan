# -*- coding:utf-8 -*-
"""
构建请求客户端, 基于tornado 的异步客户端实现
"""
from urllib.parse import urlencode
import functools
from urllib.parse import urljoin

from scrapyd_api import constants
from tornado.httpclient import HTTPRequest
from tornado.httpclient import AsyncHTTPClient


class Client(object):
    """AsyncHTTPClient 二次封装, 暴露接口分为 post, get
    """

    def __init__(self, **kwargs):
        self._username = kwargs.get('username')
        self._password = kwargs.get('password')
        self._target = kwargs.get('target', 'http://localhost:6800')
        self._timeout = kwargs.get('timeout')
        self._requests = AsyncHTTPClient()

    def _prepare_body(self, data, files=None):
        """创建post需要的body数据
        :param data: post 参数
        :type data: dict(post_param=value)
        :param: files: post 文件流数据
        :type: files: dict(filename=file_object)
        """
        data.update(files)
        return urlencode(data)

    def _http_request(self, **kwargs):
        kwargs['auth_username'] = self._username
        kwargs['auth_password'] = self._password
        kwargs['connect_timeout'] = self._timeout
        return HTTPRequest(**kwargs)

    def get(self, url, callback=None, params=None):
        """类似requests.get
            return: tornado.httpclient.HTTPResponse
        """
        if not params is None:
            url += '?' + '&'.join(["{}={}".format(i, params[i]) for i in params])
        request = self._http_request(url=urljoin(self._target, url))
        if callback is None:
            return self._requests.fetch(request)
        return self._requests.fetch(request, callback=functools.partial(callback))

    def post(self, url, callback=None, **kwargs):
        """类似requests.post
            return: tornado.httpclient.HTTPResponse
        """
        data = kwargs.get('data', {})
        files = kwargs.get('fileds', {})
        kwargs['body'] = self._prepare_body(data=data, files=files)
        try:
            kwargs.pop('data')
            kwargs.pop('fileds')
        except KeyError:
            pass
        request = self._http_request(url=urljoin(self._target, url), method="POST", **kwargs)
        if callback is None:
            return self._requests.fetch(request)
        return self._requests.fetch(request, callback=functools.partial(callback))


class ScrapyApi(object):
    """修改了scrapy_api类使得其能异步的运行

    Example usage::
        作为普通函数使用:
            def handle_response(response):
                if response.error:
                    print("Error: %s" % response.error)
                else:
                    print(response.body)
                tornado.ioloop.IOLoop.current().stop()

            scrapy_object = ScrapyApi()
            scrapy_object.list_project(callback=handle_response)
            tornado.ioloop.IOLoop.current().start()

        在tornado 框架中运行:
            class testClass(tornado.web.RequestHandler):
                async def get(self, *args, **kwargs):
                    scrapy_object = ScrapyApi()
                    response = await scrapy_object.list_project()
    """

    def __init__(self, **kwargs):
        self.target = kwargs.get('target', 'http://localhost:6800')
        self._client = Client(**kwargs)
        self._endpoints = constants.DEFAULT_ENDPOINTS

    def _build_url(self, endpoint):
        return urljoin(self.target, self._endpoints[endpoint])

    def add_version(self, project, version, egg, callback=None):
        """
        Adds a new project egg to the Scrapyd service. First class, maps to
        Scrapyd's add version endpoint.
        """
        url = self._build_url(constants.ADD_VERSION_ENDPOINT)
        data = {
            'project': project,
            'version': version,
        }
        files = {
            'egg': egg
        }
        return self._client.post(url, data=data, fileds=files, callback=callback)

    def cancel(self, project, job, signal=None, callback=None):
        """
        Cancels a job from a specific project. First class, maps to
        Scrapyd's cancel job endpoint.
        """
        url = self._build_url(constants.CANCEL_ENDPOINT)
        data = {
            'project': project,
            'job': job,
        }
        if signal is not None:
            data['signal'] = signal
        return self._client.post(url, data=data, callback=callback)

    def delete_project(self, project, callback=None):
        """
        Deletes all versions of a project. First class, maps to Scrapyd's
        delete project endpoint.
        """
        url = self._build_url(constants.DELETE_PROJECT_ENDPOINT)
        data = {
            'project': project,
        }
        return self._client.post(url, data=data, callback=callback)

    def delete_version(self, project, version, callback=None):
        """
        Deletes a specific version of a project. First class, maps to
        Scrapyd's delete version endpoint.
        """
        url = self._build_url(constants.DELETE_VERSION_ENDPOINT)
        data = {
            'project': project,
            'version': version
        }

        return self._client.post(url, data=data, callback=callback)

    def list_jobs(self, project):
        """
        Lists all known jobs for a project. First class, maps to Scrapyd's
        list jobs endpoint.
        """
        url = self._build_url(constants.LIST_JOBS_ENDPOINT)
        params = {'project': project}
        return self._client.get(url, params=params)

    def list_projects(self, callback=None):
        """
        Lists all deployed projects. First class, maps to Scrapyd's
        list projects endpoint.
        """
        url = self._build_url(constants.LIST_PROJECTS_ENDPOINT)
        return self._client.get(url, callback=callback)

    def list_spiders(self, project, callback=None):
        """
        Lists all known spiders for a specific project. First class, maps
        to Scrapyd's list spiders endpoint.
        """
        url = self._build_url(constants.LIST_SPIDERS_ENDPOINT)
        params = {'project': project}
        return self._client.get(url, params=params, callback=callback)

    def list_versions(self, project, callback=None):
        """
        Lists all deployed versions of a specific project. First class, maps
        to Scrapyd's list versions endpoint.
        """
        url = self._build_url(constants.LIST_VERSIONS_ENDPOINT)
        params = {'project': project}
        return self._client.get(url, params=params, callback=callback)

    def schedule(self, project, spider, settings=None, callback=None, **kwargs):
        """
        Schedules a spider from a specific project to run. First class, maps
        to Scrapyd's scheduling endpoint.
        """

        url = self._build_url(constants.SCHEDULE_ENDPOINT)
        data = {
            'project': project,
            'spider': spider
        }
        data.update(kwargs)
        if settings:
            setting_params = []
            for setting_name, value in settings.items():
                setting_params.append('{0}={1}'.format(setting_name, value))
            data['setting'] = setting_params
        return self._client.post(url, data=data, callback=callback)

    def spider_log(self, project_name, spider_name, spider_id, callback=None):
        """获取指定spider的日志
        """
        url = urljoin(
            self.target, '/logs/{project_name}/{spider_name}/{spider_id}.log'.format(
                project_name=project_name, spider_name=spider_name, spider_id=spider_id
            )
        )
        return self._client.get(url, callback=callback)


if __name__ == '__main__':
    Client()
