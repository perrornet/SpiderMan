__author__ = 'xsank'

import logging

import tornado.web
import tornado.websocket

from SpiderMan.server.web.views import BaseHandler
from SpiderMan.server.web.webSsh.daemon import Bridge
from SpiderMan.server.web.webSsh.data import ClientData
from SpiderMan.server.web.webSsh.utils import check_ip, check_port


class IndexHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, host_id):
        self.render("webssh.html", host_id=host_id)


class WSHandler(tornado.websocket.WebSocketHandler):
    clients = dict()

    def get_client(self):
        return self.clients.get(self._id(), None)

    def put_client(self):
        bridge = Bridge(self)
        self.clients[self._id()] = bridge

    def remove_client(self):
        bridge = self.get_client()
        if bridge:
            bridge.destroy()
            del self.clients[self._id()]

    @staticmethod
    def _check_init_param(data):
        return check_ip(data["host"]) and check_port(data["port"])

    @staticmethod
    def _is_init_data(data):
        return data.get_type() == 'init'

    def _id(self):
        return id(self)

    def open(self):
        self.put_client()

    def on_message(self, message):
        bridge = self.get_client()
        client_data = ClientData(message)
        if self._is_init_data(client_data):
            print(client_data.data)
            if self._check_init_param(client_data.data):
                bridge.open(client_data.data)
                logging.info('connection established from: %s' % self._id())
            else:
                self.remove_client()
                logging.warning('init param invalid: %s' % client_data.data)
        else:
            if bridge:
                bridge.trans_forward(client_data.data)

    def on_close(self):
        self.remove_client()
        logging.info('client close the connection: %s' % self._id())

