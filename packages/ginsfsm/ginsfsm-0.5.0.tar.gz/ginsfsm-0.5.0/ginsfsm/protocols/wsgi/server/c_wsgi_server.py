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
from ginsfsm.compat import string_types
from ginsfsm.globals import get_global_app
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
    # quiza es mejor generalizar este nivel.
    # elegir el tipo de aplicación:
    # si es un GObj enviarle el evento, sino, por defecto, sería una wsgi.
    # el evento de desconexión lo tengo solucionado: un subscribe al channel.

    channel = event.channel
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
            ('EV_HTTP_CHANNEL_OPENED',  ac_channel_opened,  None),
            ('EV_HTTP_CHANNEL_CLOSED',  ac_channel_closed,  None),
            ('EV_HTTP_REQUEST',         ac_request,         None),
        ),
    }
}

GWSGISERVER_GCONFIG = GHTTPSERVER_GCONFIG.copy()
GWSGISERVER_GCONFIG.update({
    'application': [None, None, 0, None, "wsgi application"],
})


class GWsgiServer(GObj):
    """  WSGI Server gobj.

    .. ginsfsm::
       :fsm: GWSGISERVER_FSM
       :gconfig: GWSGISERVER_GCONFIG

    *Bottom Input-Events:*

        * :attr:`'EV_HTTP_CHANNEL_OPENED'`: new http client.

          Event attributes:

            * ``channel``: http channel.

        * :attr:`'EV_HTTP_CHANNEL_CLOSED'`: http client closed.

          Event attributes:

            * ``channel``: http channel.

        * :attr:`'EV_HTTP_REQUEST'`: new http request.

          Event attributes:

            * ``channel``: http channel.
            * ``request``: http request.

        See :class:`ginsfsm.protocols.http.server.c_http_clisrv.GHttpCliSrv`.

    """

    def __init__(self):
        GObj.__init__(self, GWSGISERVER_FSM, GWSGISERVER_GCONFIG)
        self._n_connected_clisrv = 0

    def start_up(self):
        self.ghttpserver = self.create_gobj(
            self.name if self.name else 'http-server',
            GHttpServer,
            self,
            subscriber=self,
            host=self.config.host,
            port=self.config.port,
            origins=self.config.origins,
            inactivity_timeout=self.config.inactivity_timeout,
            responseless_timeout=self.config.responseless_timeout,
            maximum_simultaneous_requests=
                self.config.maximum_simultaneous_requests,
        )
        self.serversock = self.ghttpserver.gserversock.socket

        # Used in environ
        self.effective_host, self.effective_port = self.getsockname()
        self.server_name = self._get_server_name(self.config.host)

    def select_app(self, request):
        # Starting from ini file, the application references is a string
        # because the wsgi-apps are loaded later than main gaplic.
        if isinstance(self.config.application, string_types):
            self.config.application = get_global_app(self.config.application)
        return self.config.application

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
