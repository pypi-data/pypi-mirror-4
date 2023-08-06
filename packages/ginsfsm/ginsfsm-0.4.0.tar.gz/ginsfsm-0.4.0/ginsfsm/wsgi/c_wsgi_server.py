# -*- encoding: utf-8 -*-
"""
GObj :class:`GWSGIServer`
=========================

.. autoclass:: GWSGIServer
    :members:

"""

from ginsfsm.gobj import GObj
from ginsfsm.c_srv_sock import GServerSock
from ginsfsm.wsgi.c_httpchannel import HTTPChannel


def ac_new_httpchannel(self, event):
    """ New gsock clisvr, create a new httpchannel
    """
    self._n_connected_clisrv += 1
    gsock = event.source[-1]  # new gsock clisrv

    if self.name and len(self.name):
        prefix_name = self.name
    else:
        prefix_name = None
    self.serversock = self.create_gobj(
        prefix_name + '.http-channel' if prefix_name else None,
        HTTPChannel,
        self,
        wsgi_server=self,
        gsock=gsock,
    )


def ac_drop_httpchannel(self, event):
    """ httpchannel closed, drop it.
    """
    # TODO: need to drop gsock, httpchannel and wsgiapp
    channel = event.source[-1]
    self._n_connected_clisrv -= 1
    self.destroy_gobj(channel)


def ac_timeout(self, event):
    self.set_timeout(10)
    print "Server's clients: %d, connected %d" % (
        len(self.dl_childs), self._n_connected_clisrv)


GWSGISERVER_FSM = {
    'event_list': (
        'EV_SET_TIMER: bottom output',
        'EV_TIMEOUT: bottom input',
        'EV_CONNECTED: bottom input',
        'EV_DISCONNECTED: bottom input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',          ac_timeout,             None),
            ('EV_CONNECTED',        ac_new_httpchannel,     None),
            ('EV_DISCONNECTED',     ac_drop_httpchannel,    None),
        ),
    }
}

GWSGISERVER_GCONFIG = {
    'host': [str, '', 0, None, "listening host"],
    'port': [int, 0, 0, None, "listening port"],
    'origins': [None, None, 0, None,
        "TODO:list of (host, port) tuples allowed to connect from"],
    #TODO: implement a multi wsgi application
    'application': [None, None, 0, None, "wsgi application"],
    'url_scheme': [str, 'http', 0, None, "default ``wsgi.url_scheme`` value"],
    'identity': [str, 'ginsfsm', 0, None,
                 "server identity (sent in Server: header)"],
}


class GWSGIServer(GObj):
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
        self.serversock = self.create_gobj(
            prefix_name + '.sock-server' if prefix_name else None,
            GServerSock,
            self,
            subscriber=self,
            host=self.host,
            port=self.port,
            origins=self.origins,
        )

        # Used in environ
        self.effective_host, self.effective_port = \
            self.serversock.getsockname()
        self.server_name = self._get_server_name(self.host)

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
        return self.serversock.socket.getsockname()
