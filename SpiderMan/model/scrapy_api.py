# -*- coding:utf-8 -*-
import requests

from scrapyd_api import ScrapydAPI
from scrapyd_api.compat import urljoin
from scrapyd_api.exceptions import ScrapydResponseError


def base_url(host, port):
    """build scrapyd host url
    :param host: scrapyd host ip
    :param port: scrapyd host port
    :return scrapyd host url
    """
    return 'http://{host}:{port}'.format(host=host, port=port)


class Client(requests.Session):
    """
    The client is a thin wrapper around the requests Session class which
    allows us to wrap the response handler so that we can handle it in a
    Scrapyd-specific way.
    """
    def __init__(self, timeout):
        super(Client, self).__init__()
        self.timeout = timeout

    def _handle_response(self, response):
        """
        Handles the response received from Scrapyd.
        """
        if not response.ok:
            raise ScrapydResponseError(
                "Scrapyd returned a {0} error: {1}".format(
                    response.status_code,
                    response.text))

        try:
            json = response.json()
        except ValueError:
            return response.content
        if json['status'] == 'ok':
            json.pop('status')
            return json
        elif json['status'] == 'error':
            raise ScrapydResponseError(json['message'])

    def request(self, *args, **kwargs):
        kwargs['timeout'] = self.timeout
        response = super(Client, self).request(*args, **kwargs)
        return self._handle_response(response)


class ScrapydAPI_(ScrapydAPI):
    """Further encapsulation of ScrapydAPI
    """
    def __init__(self, target='http://localhost:6800', auth=None, endpoints=None, timeout=10):
        super(ScrapydAPI_, self).__init__(target, auth, endpoints, Client(timeout=timeout))

    def spider_log(self, project_name, spider_name, spider_id):
        url = urljoin(self.target, '/logs/{project_name}/{spider_name}/{spider_id}.log'. \
                      format(project_name=project_name, spider_name=spider_name, spider_id=spider_id))
        return self.client.get(url)
