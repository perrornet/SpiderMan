# -*- coding:utf-8 -*-
import traceback
import json
import time
import hashlib
import tornado.web
from tornado import gen
from tornado import escape
from tornado.log import app_log
from tornado.escape import utf8
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest

from SpiderMan.util.model_to_dict import ModelsToDict


class BaseHandler(tornado.web.RequestHandler):
    """所有API的基类, 实现获取所有的参数, 统一的错误返回
    """

    @gen.coroutine
    def _execute(self, transforms, *args, **kwargs):
        """Executes this request with the given output transforms. 修改此类实现未捕获的错误能顺利返回"""
        self._transforms = transforms
        try:
            if self.request.method not in self.SUPPORTED_METHODS:
                raise tornado.web.HTTPError(405)
            self.path_args = [self.decode_argument(arg) for arg in args]
            self.path_kwargs = dict((k, self.decode_argument(v, name=k))
                                    for (k, v) in kwargs.items())
            # If XSRF cookies are turned on, reject form submissions without
            # the proper cookie
            if self.request.method not in ("GET", "HEAD", "OPTIONS") and \
                    self.application.settings.get("xsrf_cookies"):
                self.check_xsrf_cookie()

            result = self.prepare()
            if result is not None:
                result = yield result
            if self._prepared_future is not None:
                # Tell the Application we've finished with prepare()
                # and are ready for the body to arrive.
                tornado.web.future_set_result_unless_cancelled(self._prepared_future, None)
            if self._finished:
                return

            if tornado.web._has_stream_request_body(self.__class__):
                # In streaming mode request.body is a Future that signals
                # the body has been completely received.  The Future has no
                # result; the data has been passed to self.data_received
                # instead.
                try:
                    yield self.request.body
                except tornado.web.iostream.StreamClosedError:
                    return

            method = getattr(self, self.request.method.lower())
            try:
                result = method(*self.path_args, **self.path_kwargs)
            except Exception as f:
                self.write({"data": False, "msg": str(f)}, status_code=500)
                app_log.error(traceback.format_exc())
            if result is not None:
                try:
                    result = yield result
                except Exception as f:
                    self.write({"data": False, "msg": str(f)}, status_code=500)
                    app_log.error(traceback.format_exc())
            if self._auto_finish and not self._finished:
                self.finish()
        except Exception as e:
            try:
                self._handle_request_exception(e)
            except Exception:
                app_log.error("Exception in exception handler", exc_info=True)
            finally:
                # Unset result to avoid circular references
                result = None
            if (self._prepared_future is not None and
                    not self._prepared_future.done()):
                # In case we failed before setting _prepared_future, do it
                # now (to unblock the HTTP server).  Note that this is not
                # in a finally block to avoid GC issues prior to Python 3.4.
                self._prepared_future.set_result(None)

    def write(self, chunk, status_code=200):
        if self._finished:
            raise RuntimeError("Cannot write() after finish()")
        if isinstance(chunk, dict):
            if 'msg' not in chunk:
                chunk.update(msg="")
            if isinstance(chunk['data'], ModelsToDict):
                chunk['data'] = chunk['data'].data
            chunk = json.dumps(chunk, ensure_ascii=False)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        chunk = utf8(chunk)

        self._write_buffer.append(chunk)
        self.set_status(status_code=status_code)

    async def ping(self, url):
        try:
            print(url)
            response = await AsyncHTTPClient().fetch(HTTPRequest(url=url, connect_timeout=0.2))
        except tornado.httpclient.HTTPError:
            return False
        except:
            return False
        if response.code // 100 != 2:
            return False
        return True

    def get_all_argument(self):
        data = {}
        for i in self.request.body.decode().split('&'):
            _, data[_] = i.split("=")
            data[_] = escape.url_unescape(data[_])
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

    def time2time(self, x):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x))
