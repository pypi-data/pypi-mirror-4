# -*- encoding: utf-8 -*-
"""
    AsyncResponse -  an asynchronous WebOb Response over ginsfsm.
"""
import logging

from ginsfsm.protocols.http.server.c_http_clisrv import ResponseInterrupt

try:
    from pyramid.response import Response
except ImportError:  # pragma: no cover
    try:
        from webob import Response
    except ImportError:  # pragma: no cover
        raise Exception('async_response is depending of Pyramid or WebOb')


class AsyncResponse(Response):
    def __init__(self, **kw):
        super(AsyncResponse, self).__init__(**kw)
        self.ginsfsm_channel = None

        del self.app_iter  # Important trick to remove Content-Length.
        # WARNING: you cannot use body, because it sets Content-Length.

    def __call__(self, environ, start_response):
        "Override WSGI call"
        self.ginsfsm_channel = environ['ginsfsm.channel']

        start_response(self.status, self._abs_headerlist(environ))

        # send the current body to the network
        for chunk in self.app_iter:
            self.write(chunk)
            self.flush()
        del self.app_iter

        raise ResponseInterrupt()

    def write(self, data):
        """ Write data to http channel.
        """
        if self.ginsfsm_channel:
            self.ginsfsm_channel.write(data)
        else:
            # write in the sync response by now.
            # in wsgi response call, all app_iter will be flush.
            super(AsyncResponse, self).write(data)

    def flush(self, callback=None):
        """Flushes the current output buffer to the network.

        The ``callback`` argument, if given, can be used for flow control:
        it will be run when all flushed data has been written to the socket.
        Note that only one flush callback can be outstanding at a time;
        if another flush occurs before the previous flush's callback
        has been run, the previous callback will be discarded.
        """
        if self.ginsfsm_channel:
            self.ginsfsm_channel.flush(callback)
        else:
            logging.error('ERROR async Flush before set ginsfsm_channel')

    def finish(self):
        """Finishes this response, ending the HTTP request."""
        if self.ginsfsm_channel:
            self.ginsfsm_channel.finish()
        else:
            logging.error('ERROR async FINISH before set ginsfsm_channel')
