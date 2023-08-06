# -*- encoding: utf-8 -*-
"""
GObj :class:`WsgiResponse`
===========================

Code copied from waitress.task.py adapted to ginsfsm.

.. autoclass:: HttpResponse
    :members:

"""

import logging
import sys
from ginsfsm.deferred import DeferredInterrupt
from ginsfsm.buffers import ReadOnlyFileBasedBuffer
from ginsfsm.compat import (
    reraise,
)
from ginsfsm.protocols.http.common.response import HttpResponse

rename_headers = {
    'CONTENT_LENGTH' : 'CONTENT_LENGTH',
    'CONTENT_TYPE'   : 'CONTENT_TYPE',
    'CONNECTION'     : 'CONNECTION_TYPE',
    }

hop_by_hop = frozenset((
    'connection',
    'keep-alive',
    'proxy-authenticate',
    'proxy-authorization',
    'te',
    'trailers',
    'transfer-encoding',
    'upgrade'
    ))


class WsgiResponse(HttpResponse):
    """Get a response from a WSGI application.
    """
    environ = None

    def __init__(self, request, wsgi_server, application):
        HttpResponse.__init__(self, request)
        self.wsgi_server = wsgi_server
        self.application = application

    def execute(self):
        env = self.get_environment()

        def start_response(status, headers, exc_info=None):
            if self.complete and not exc_info:
                raise AssertionError("start_response called a second time "
                                     "without providing exc_info.")
            if exc_info:
                try:
                    if self.complete:
                        # higher levels will catch and handle raised exception:
                        # 1. "service" method in task.py
                        # 2. "service" method in gsock.py
                        # 3. "handler_thread" method in task.py
                        reraise(exc_info[0], exc_info[1], exc_info[2])
                    else:
                        # As per WSGI spec existing headers must be cleared
                        self.response_headers = []
                finally:
                    exc_info = None

            self.complete = True

            if not status.__class__ is str:
                raise AssertionError('status %s is not a string' % status)

            self.status = status

            # Prepare the headers for output
            for k, v in headers:
                if not k.__class__ is str:
                    raise AssertionError(
                        'Header name %r is not a string in %r' % (k, (k, v))
                        )
                if not v.__class__ is str:
                    raise AssertionError(
                        'Header value %r is not a string in %r' % (v, (k, v))
                        )
                kl = k.lower()
                if kl == 'content-length':
                    self.content_length = int(v)
                elif kl in hop_by_hop:
                    raise AssertionError(
                        '%s is a "hop-by-hop" header; it cannot be used by '
                        'a WSGI application (see PEP 3333)' % k)

            self.response_headers.extend(headers)

            # Return a method used to write the response data.
            return self.write

        # Call the application to handle the request and write a response
        # TODO: do a multi wsgi-app
        try:
            app_iter = self.application(env, start_response)
        except DeferredInterrupt:
            """ A gobj inside his gaplic need
                to wait for data from another gaplic.
            """
            raise

        try:
            if app_iter.__class__ is ReadOnlyFileBasedBuffer:
                cl = self.content_length
                size = app_iter.prepare(cl)
                if size:
                    if cl != size:
                        if cl is not None:
                            self.remove_content_length_header()
                        self.content_length = size
                    self.write(b'')  # generate headers
                    self.gsock.write_soon(app_iter)
                    return

            first_chunk_len = None
            for chunk in app_iter:
                if first_chunk_len is None:
                    first_chunk_len = len(chunk)
                    # Set a Content-Length header if one is not supplied.
                    # start_response may not have been called until first
                    # iteration as per PEP, so we must reinterrogate
                    # self.content_length here
                    if self.content_length is None:
                        app_iter_len = None
                        if hasattr(app_iter, '__len__'):
                            app_iter_len = len(app_iter)
                        if app_iter_len == 1:
                            self.content_length = first_chunk_len
                # transmit headers only after first iteration of the iterable
                # that returns a non-empty bytestring (PEP 3333)
                if chunk:
                    self.write(chunk)

            cl = self.content_length
            if cl is not None:
                if self.content_bytes_written != cl:
                    # close the connection so the client isn't sitting around
                    # waiting for more data when there are too few bytes
                    # to service content-length
                    self.close_on_finish = True
                    logging.error(
                        'application returned too few bytes (%s) '
                        'for specified Content-Length (%s) via app_iter' % (
                            self.content_bytes_written, cl),
                        )
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()

    def get_environment(self):
        """Returns a WSGI environment."""
        environ = self.environ
        if environ is not None:
            # Return the cached copy.
            return environ

        request = self.request
        path = request.path
        channel = request.channel
        gsock = request.channel.gsock
        wsgi_server = self.wsgi_server

        while path and path.startswith('/'):
            path = path[1:]

        environ = {}
        # Own variables to do asynchronous response
        environ['channel'] = channel
        environ['gaplic'] = channel.gaplic
        #environ['ext_event'] = self.ext_event

        environ['REQUEST_METHOD'] = request.command.upper()
        environ['SERVER_PORT'] = str(wsgi_server.effective_port)
        environ['SERVER_NAME'] = wsgi_server.server_name
        environ['SERVER_SOFTWARE'] = wsgi_server.identity
        environ['SERVER_PROTOCOL'] = 'HTTP/%s' % self.version
        environ['SCRIPT_NAME'] = ''
        environ['PATH_INFO'] = '/' + path
        environ['QUERY_STRING'] = request.query
        environ['REMOTE_ADDR'] = gsock.addr[0]

        for key, value in request.headers.items():
            value = value.strip()
            mykey = rename_headers.get(key, None)
            if mykey is None:
                mykey = 'HTTP_%s' % key
            if not mykey in environ:
                environ[mykey] = value

        # the following environment variables are required by the WSGI spec
        environ['wsgi.version'] = (1, 0)
        environ['wsgi.url_scheme'] = request.url_scheme
        environ['wsgi.errors'] = sys.stderr  # apps should use the logging module
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = False
        environ['wsgi.run_once'] = False
        environ['wsgi.input'] = request.get_body_stream()
        environ['wsgi.file_wrapper'] = ReadOnlyFileBasedBuffer

        self.environ = environ
        return environ
