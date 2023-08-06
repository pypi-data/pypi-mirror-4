# -*- encoding: utf-8 -*-
"""
GObj :class:`GHttpServer`
=========================

.. autoclass:: GHttpServer
    :members:

"""
try:
    import ssl  # Python 2.6+
except ImportError:
    ssl = None

from ginsfsm.gobj import GObj
from ginsfsm.c_srv_sock import GServerSock
from ginsfsm.protocols.http.server.c_http_clisrv import GHttpCliSrv


def ac_connected(self, event):
    """ New clisvr gsock (http channel):
    A new client http has been acepted.
    The new clisrv GSock, created by GServerSock is sending this event.
    """
    self._n_connected_clisrv += 1
    gsock = event.source[-1]
    gsock.delete_all_subscriptions()

    if self.name:
        prefix_name = self.name
    else:
        prefix_name = None
    channel = '.http.%s' % gsock.name
    clisrv = self.create_gobj(
        prefix_name + channel if prefix_name else None,
        GHttpCliSrv,
        self,
        gsock=gsock,
        subscriber=self.subscriber,  # TODO better to join two configs
        identity=self.identity,
        maximum_simultaneous_requests=self.maximum_simultaneous_requests,
        url_scheme=self.url_scheme,
        inactivity_timeout=self.inactivity_timeout,
        responseless_timeout=self.responseless_timeout,
        inbuf_overflow=self.inbuf_overflow,
        max_request_header_size=self.max_request_header_size,
        max_request_body_size=self.max_request_body_size,
    )
    clisrv.subscribe_event('EV_HTTP_CHANNEL_CLOSED', self)


def ac_disconnected(self, event):
    """ **Some** clisvr gsock closed, drop it.
    """
    gobj = event.source[-1]
    self.post_event(self, 'EV_DESTROY_CLISRV', gobj=gobj)


def ac_drop_httpchannel(self, event):
    """ It's better receive this event by post_event().
    """
    gobj = event.gobj
    self._n_connected_clisrv -= 1
    self.destroy_gobj(gobj)


def ac_timeout(self, event):
    self.set_timeout(10)
    print "Server's clients: %d, connected %d" % (
        len(self.dl_childs), self._n_connected_clisrv)


GHTTPSERVER_FSM = {
    'event_list': (
        'EV_CONNECTED: bottom input',
        'EV_HTTP_CHANNEL_CLOSED: bottom input',
        'EV_TIMEOUT',
        'EV_DESTROY_CLISRV',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',              ac_timeout,             None),
            ('EV_CONNECTED',            ac_connected,           None),
            ('EV_HTTP_CHANNEL_CLOSED',  ac_disconnected,        None),
            ('EV_DESTROY_CLISRV',       ac_drop_httpchannel,    None),
        ),
    }
}

GHTTPSERVER_GCONFIG = {
    'subscriber': [None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
        ],
    'host': [str, '', 0, None, "listening host"],
    'port': [int, 0, 0, None, "listening port"],
    'origins': [None, None, 0, None,
        "TODO:list of (host, port) tuples allowed to connect from"],

    'expose_tracebacks': [bool, False, 0, None,
        "expose tracebacks of uncaught exceptions"],
    'maximum_simultaneous_requests': [int, 0, 0, None,
        "maximum simultaneous requests. Default: 0, without limit."
        ],
    'identity': [str, 'ginsfsm', 0, None,
        "server identity (sent in Server: header)"
        ],
    'url_scheme': [str, 'http', 0, None, "default ``http`` value"],
    'inactivity_timeout': [int, 5 * 60 * 60, 0, None,
        "Inactivity timeout in seconds."
        ],
    'responseless_timeout': [int, 5 * 60 * 60, 0, None,
        "'Without response' timeout in seconds."
        ],
    # A tempfile should be created if the pending input is larger than
    # inbuf_overflow, which is measured in bytes. The default is 512K.  This
    # is conservative.
    'inbuf_overflow': [int, 524288, 0, None, ""],
    # maximum number of bytes of all request headers combined (256K default)
    'max_request_header_size': [int, 262144, 0, None, ""],
    # maximum number of bytes in request body (1GB default)
    'max_request_body_size': [int, 1073741824, 0, None, ""],
}


class GHttpServer(GObj):
    """  Asynchronous Http Server gobj.

    In the startup, this class creates internally a server socket, gobj of
    :class:`ginsfsm.c_srv_sock.GServerSock` gclass.

    When a new client connects,
    a new :class:`ginsfsm.c_sock.GSock` gobj is created,
    receiving the EV_CONNECTED event.
    Then it creates a
    :class:`ginsfsm.protocols.http.server.c_http_clisrv.GHttpCliSrv` gobj
    that will process all the events of the GSock gobj.

    The output events of
    :class:`ginsfsm.protocols.http.server.c_http_clisrv.GHttpCliSrv`
    will be processed by ``subscriber`` gobj of this class.

    .. ginsfsm::
       :fsm: GHTTPSERVER_FSM
       :gconfig: GHTTPSERVER_GCONFIG

    *Input-Events:*
        * :attr:`'EV_CONNECTED'`: new *clisrv*, client socket.

          The internal child :class:`ginsfsm.c_srv_sock.GServerSock` gobj
          has accepted a new socket connection,
          and it has created a new client gobj (*clisrv*) of
          :class:`ginsfsm.c_sock.GSock` gclass.

          This event has been sended
          by the new :class:`ginsfsm.c_sock.GSock` *clisrv* gobj.

          A new
          :class:`ginsfsm.protocols.http.server.c_http_clisrv.GHttpCliSrv` gobj
          is created, to process all the events of the GSock gobj.

          This class will be subscred to the ``'EV_HTTP_CHANNEL_CLOSED'`` event
          in order to destroy the GHttpCliSrv gobj.

          Event attributes:

            * ``peername``: remote address to which the socket is connected.
            * ``sockname``: the socket’s own address.


        * :attr:`'EV_HTTP_CHANNEL_CLOSED'`: http channel disconnected.

          The http server subcribes this event from clisrv gobj,
          in order to destroy it when became disconnected.
    """

    def __init__(self):
        GObj.__init__(self, GHTTPSERVER_FSM, GHTTPSERVER_GCONFIG)
        self._n_connected_clisrv = 0

    def start_up(self):
        if self.name:
            prefix_name = self.name
        else:
            prefix_name = None
        self.gserversock = self.create_gobj(
            prefix_name + '.http-server' if prefix_name else None,
            GServerSock,
            self,
            subscriber=self,  # Iniatially capture all events from new clisrv.
            host=self.host,
            port=self.port,
        )

    def _get_ssl_certificate(self, binary_form=False):
        """Returns the client's SSL certificate, if any.

        To use client certificates, the HTTPServer must have been constructed
        with cert_reqs set in ssl_options, e.g.::

            server = HTTPServer(app,
                ssl_options=dict(
                    certfile="foo.crt",
                    keyfile="foo.key",
                    cert_reqs=ssl.CERT_REQUIRED,
                    ca_certs="cacert.crt"))

        By default, the return value is a dictionary (or None, if no
        client certificate is present).  If ``binary_form`` is true, a
        DER-encoded form of the certificate is returned instead.  See
        SSLSocket.getpeercert() in the standard library for more
        details.
        http://docs.python.org/library/ssl.html#sslsocket-objects
        """
        try:
            return self.connection.stream.socket.getpeercert(
                binary_form=binary_form)
        except ssl.SSLError:
            return None
