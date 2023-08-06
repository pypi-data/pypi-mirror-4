# -*- encoding: utf-8 -*-
"""
GObj :class:`GWsgiServer`
=========================

WSGI server.

It uses :class:`ginsfsm.protocols.http.server.c_http_server.GHttpServer`.

.. autoclass:: GWsgiServer
    :members:

"""

from ginsfsm.gobj import GObj
from ginsfsm.protocols.http.server.c_http_server import GHttpServer
from ginsfsm.protocols.wsgi.common.wsgi_response import WsgiResponse
from ginsfsm.protocols.http.server.c_http_server import GHTTPSERVER_GCONFIG


def ac_channel_opened(self, event):
    """ New client opened.
    """


def ac_channel_closed(self, event):
    """ Client closed.
    """


def ac_request(self, event):
    channel = event.source[-1]
    request = event.request
    application = self.select_app(request)
    response = WsgiResponse(request, self, application)
    self.send_event(channel, 'EV_HTTP_RESPONSE', response=response)


GWSGISERVER_FSM = {
    'event_list': (
        'EV_HTTP_CHANNEL_OPENED: bottom input',
        'EV_HTTP_CHANNEL_CLOSED: bottom input',
        'EV_HTTP_REQUEST: bottom input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_HTTP_CHANNEL_OPENED',  ac_channel_opened,  'ST_IDLE'),
            ('EV_HTTP_CHANNEL_CLOSED',  ac_channel_closed,  'ST_IDLE'),
            ('EV_HTTP_REQUEST',         ac_request,         'ST_IDLE'),
        ),
    }
}

GWSGISERVER_GCONFIG = GHTTPSERVER_GCONFIG.copy()
GWSGISERVER_GCONFIG.update({
    #TODO: implement a multi wsgi application
    'application': [None, None, 0, None, "wsgi application"],
})


class GWsgiServer(GObj):
    """  WSGI Server gobj.

    The incoming connections will create a new :class:`ginsfsm.c_sock.GSock`
    :term:`gobj`,
    that will be child of the :attr:`subscriber` :term:`gobj`.

        .. warning::  Remember destroy the accepted `gobj`
           with :func:`destroy_gobj` when the `gobj` has been disconnected.

           The `subcriber` knows when a new `gobj` has been accepted because it
           receives the ``'EV_CONNECTED'`` event.

           When the `subcriber` receives a ``'EV_DISCONNECTED'`` event must
           destroy the `gobj` because the connection ceases to exist.

    .. ginsfsm::
       :fsm: GWSGISERVER_FSM
       :gconfig: GWSGISERVER_GCONFIG

    *Input-Events:*

        The relationship is directly between the
        accepted :class:`ginsfsm.c_sock.GSock` gobj and the :attr:`subscriber`.

        See :class:`ginsfsm.c_sock.GSock` `input-events`.

    *Output-Events:*

        The relationship is directly between the
        accepted :class:`ginsfsm.c_sock.GSock` gobj and the :attr:`subscriber`.

        See :class:`ginsfsm.c_sock.GSock` `output-events`.
    """

    def __init__(self):
        GObj.__init__(self, GWSGISERVER_FSM, GWSGISERVER_GCONFIG)
        self._n_connected_clisrv = 0

    def start_up(self):
        if self.name and len(self.name):
            prefix_name = self.name
        else:
            prefix_name = None

        self.ghttpserver = self.create_gobj(
            prefix_name + '.sock-server' if prefix_name else None,
            GHttpServer,
            self,
            subscriber=self,
            host=self.host,
            port=self.port,
            origins=self.origins,
            inactivity_timeout=10,
            responseless_timeout=2,
            maximum_simultaneous_requests=0,
        )
        self.serversock = self.ghttpserver.gserversock.socket

        # Used in environ
        self.effective_host, self.effective_port = self.getsockname()
        self.server_name = self._get_server_name(self.host)

    def select_app(self, request):
        # TODO: do a multi-app, application based on url?
        # con sistema de registro de aplicacion/url
        # una wsgi-app podria ser la puerta de injección de eventos
        # sería multi-wsgi-app en paralelo, no en pila como con los wsgi middleware
        return self.application

    def _get_server_name(self, ip):
        """Given an IP or hostname, try to determine the server name."""
        if ip:
            srv_name = str(ip)
        else:
            srv_name = str(self.serversock.socketmod.gethostname())
        # Convert to a host name if necessary.
        for c in srv_name:
            if c != '.' and not c.isdigit():
                return srv_name
        try:
            if srv_name == '0.0.0.0':
                return 'localhost'
            srv_name = self.serversock.socketmod.gethostbyaddr(srv_name)[0]
        except:
            pass
        return srv_name

    def getsockname(self):
        return self.serversock.getsockname()
