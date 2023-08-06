# -*- encoding: utf-8 -*-
"""
GObj :class:`GServerSock`
=========================

GObj for manage server socket.

.. autoclass:: GServerSock
    :members:

"""
try:
    import ssl  # Python 2.6+
except ImportError:
    ssl = None

import logging
import errno
import socket
from ginsfsm.c_sock import (
    GSock,
    GSSLSock
)

GSERVERSOCK_FSM = {  # ONLY for documentation. Partial use of GSOCK_FSM.
    'event_list': (
        'EV_CONNECTED: top output',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
        ),
    }
}

GSERVERSOCK_GCONFIG = {  # ONLY for documentation. Partial use of GSOCK_CONFIG.
    'subscriber': [None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
        ],
    'host': [str, '', 0, None, "server host (ip or name)"],
    'port': [int, 0, 0, None, "server port"],
    'ssl_options': [dict, {}, 0, None, "ssl options"],
}


class GServerSock(GSock):
    """  GSock gobj acting as server sock.

    This gobj is derived from :class:`ginsfsm.c_sock.GSock`,
    but it uses the server behaviour of a sock.
    It creates a listening sock at configured (host, port) attributes.

    `GServerSock` can serve SSL traffic with Python 2.6+ and OpenSSL.
    To make this server serve SSL traffic, send the ssl_options dictionary
    argument with the arguments required for the `ssl.wrap_socket` method,
    including "certfile" and "keyfile"::

       ssl_options={
           "certfile": os.path.join(data_dir, "mydomain.crt"),
           "keyfile": os.path.join(data_dir, "mydomain.key"),
       }

    Each incoming connection
    will create a new :class:`ginsfsm.c_sock.GSock` :term:`gobj`,
    that it will be child of the :attr:`subscriber` `gobj`
    (the parent by default).

        .. note:: Once an ``'EV_CONNECTED'`` event has been sent,
           the GServerSock
           doesn't know anything more of the new gsock client.

           The relationship is directly between the
           accepted :class:`ginsfsm.c_sock.GSock` gobj
           and the :attr:`subscriber`.

           The `subcriber` is responsible of receiving all events
           and destroy the new gsock client.


        .. warning::  Remember to destroy the accepted `gobj`
           with :func:`destroy_gobj` when the `gobj` has been disconnected.

           The `subcriber` knows when a new `gobj` has been accepted because it
           receives the ``'EV_CONNECTED'`` event.

           When the `subcriber` receives a ``'EV_DISCONNECTED'`` event must
           destroy the `gobj` because the connection ceases to exist.

    .. ginsfsm::
       :fsm: GSERVERSOCK_FSM
       :gconfig: GSERVERSOCK_GCONFIG

    *Output-Events:*
        * :attr:`'EV_CONNECTED'`: new client socket connected.

          The gobj sending the `'EV_CONNECTED'` event
          is the new client socket gobj.

          Attributes added to the sent :term:`event`:

            * ``peername``: remote address to which the socket is connected.
            * ``sockname``: the socket’s own address.

          The :attr:`subscriber` can know from which server comes the client
          by the name of client gobj.

          If the server gobj has name, the name of client gobj will be:
          'server-name.clisrv-gsock-#'
    """

    def __init__(self):
        GSock.__init__(self)
        self._n_clisrv = 0

    def start_up(self):
        """ Initialization zone.

        Subscribe all events to parent if :attr:`subscriber` is None.

        Start listen to (host,port).
        """
        if self.subscriber is None:
            self.subscriber = self.parent
        self.do_listen()

    def do_listen(self):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.host, self.port))
        logging.info("Listening '%s' host '%s', port %d..." %
                 (self.name, self.host, self.port))
        self.listen(1024)

    def handle_accepted(self, sock, addr):
        # The socket options to set on receiving a connection.
        # It is a list of (level, optname, value) tuples.
        # TCP_NODELAY disables the Nagle algorithm for writes
        # (Waitress already buffers its writes).
        # TODO: check origins for permitted source ip.
        socket_options = [
            (socket.SOL_TCP, socket.TCP_NODELAY, 1),
            ]
        for (level, optname, value) in socket_options:
            sock.setsockopt(level, optname, value)

        # copied from tornado.netutil.py
        if self.ssl_options:
            assert ssl, "Python 2.6+ and OpenSSL required for SSL"
            try:
                sock = ssl.wrap_socket(
                    sock,
                    server_side=True,
                    do_handshake_on_connect=False,
                    **self.ssl_options
                )
            except ssl.SSLError, err:
                if err.args[0] == ssl.SSL_ERROR_EOF:
                    return sock.close()
                else:
                    raise
            except socket.error, err:
                if err.args[0] == errno.ECONNABORTED:
                    return sock.close()
                else:
                    raise

        self._n_clisrv += 1
        if self.name:
            prefix_name = self.name
        else:
            prefix_name = None
        channel = '.clisrv-gsock-%x' % self._n_clisrv

        if self.ssl_options:
            gsock_class = GSSLSock
        else:
            gsock_class = GSock
        clisrv = self.create_gobj(
            prefix_name + channel if prefix_name else None,
            gsock_class,
            self.subscriber,
        )
        clisrv.set_clisrv_socket(sock)
        clisrv.handle_connect()
