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


class TickerConnection(SockJSConnection):
    def on_open(self, info):
        self.timeout = self.gaplic.PeriodicCallback(self._ticker, 1000)
        self.timeout.start()

    def on_close(self):
        self.timeout.stop()

    def _ticker(self):
        self.send('tick!')


class BroadcastConnection(SockJSConnection):
    clients = set()

    def on_open(self, info):
        self.clients.add(self)

    def on_message(self, msg):
        self.broadcast(self.clients, msg)

    def on_close(self):
        self.clients.remove(self)


class AmplifyConnection(SockJSConnection):
    def on_message(self, msg):
        n = int(msg)
        if n < 0 or n > 19:
            n = 1

        self.send('x' * int(math.pow(2, n)))


class CookieEcho(SockJSConnection):
    def on_message(self, msg):
        self.send(msg)
