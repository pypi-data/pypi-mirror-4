# -*- encoding: utf-8 -*-
""" SockJSConnection GObj

.. autoclass:: SockJSConnection
    :members: start_up

"""

import math

from ginsfsm.protocols.sockjs.server.conn import SockJSConnection


class EchoConnection(SockJSConnection):
    def on_message(self, msg):
        self.send(msg)


class CloseConnection(SockJSConnection):
    def on_open(self, info):
        self.close()

    def on_message(self, msg):
        pass


class CookieEcho(SockJSConnection):
    def on_message(self, msg):
        self.send(msg)
