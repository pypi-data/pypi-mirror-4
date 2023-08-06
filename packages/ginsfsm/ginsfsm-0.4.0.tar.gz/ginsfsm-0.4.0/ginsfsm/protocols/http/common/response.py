# -*- encoding: utf-8 -*-
"""
GObj :class:`HttpResponse`
=========================

Code copied from waitress.task.py adapted to ginsfsm.

.. autoclass:: HttpResponse
    :members:

"""

import logging
import socket
import time
from ginsfsm.deferred import DeferredInterrupt

from ginsfsm.compat import (
    tobytes,
)

from ginsfsm.protocols.http.common.utilities import (
    build_http_date,
)

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


class HttpResponse(object):
    def __init__(self, request):
        self.request = request
        self.gsock = request.channel.gsock
        self.channel = request.channel
        self.response_headers = []
        version = request.version
        if version not in ('1.0', '1.1'):
            # fall back to a version we support.
            version = '1.0'
        self.version = version

        # these variables were in the class section
        self.close_on_finish = False
        self.status = '200 OK'
        self.wrote_header = False
        self.start_time = 0
        self.content_length = None
        self.content_bytes_written = 0
        self.logged_write_excess = False
        self.complete = False
        self.chunked_response = False

    def service(self):
        try:
            try:
                self.start()
                self.execute()
                self.finish()
            except socket.error:
                self.close_on_finish = True
                raise  # ??? if self.gsock.adj.log_socket_errors:
        except DeferredInterrupt:
            raise
        finally:
            pass

    def build_response_header(self):
        version = self.version
        # Figure out whether the connection should be closed.
        connection = self.request.headers.get('CONNECTION', '').lower()
        response_headers = self.response_headers
        content_length_header = None
        date_header = None
        server_header = None
        connection_close_header = None

        for i, (headername, headerval) in enumerate(response_headers):
            headername = '-'.join(
                [x.capitalize() for x in headername.split('-')]
                )
            if headername == 'Content-Length':
                content_length_header = headerval
            if headername == 'Date':
                date_header = headerval
            if headername == 'Server':
                server_header = headerval
            if headername == 'Connection':
                connection_close_header = headerval.lower()
            # replace with properly capitalized version
            response_headers[i] = (headername, headerval)

        if content_length_header is None and self.content_length is not None:
            content_length_header = str(self.content_length)
            self.response_headers.append(
                ('Content-Length', content_length_header)
                )

        def close_on_finish():
            if connection_close_header is None:
                response_headers.append(('Connection', 'close'))
            self.close_on_finish = True

        if version == '1.0':
            if connection == 'keep-alive':
                if not content_length_header:
                    close_on_finish()
                else:
                    response_headers.append(('Connection', 'Keep-Alive'))
            else:
                close_on_finish()

        elif version == '1.1':
            if connection == 'close':
                close_on_finish()

            if not content_length_header:
                response_headers.append(('Transfer-Encoding', 'chunked'))
                self.chunked_response = True
                if not self.close_on_finish:
                    close_on_finish()

            # under HTTP 1.1 keep-alive is default, no need to set the header
        else:
            raise AssertionError('neither HTTP/1.0 or HTTP/1.1')

        # Set the Server and Date field, if not yet specified. This is needed
        # if the server is used as a proxy.
        ident = self.request.channel.identity
        if not server_header:
            response_headers.append(('Server', ident))
        else:
            response_headers.append(('Via', ident))
        if not date_header:
            response_headers.append(('Date', build_http_date(self.start_time)))

        first_line = 'HTTP/%s %s' % (self.version, self.status)
        next_lines = ['%s: %s' % hv for hv in sorted(self.response_headers)]
        lines = [first_line] + next_lines
        res = '%s\r\n\r\n' % '\r\n'.join(lines)
        return tobytes(res)

    def remove_content_length_header(self):
        for i, (header_name, header_value) in enumerate(self.response_headers):
            if header_name.lower() == 'content-length':
                del self.response_headers[i]

    def start(self):
        self.start_time = time.time()

    def finish(self):
        if not self.wrote_header:
            self.write(b'')
        if self.chunked_response:
            # not self.write, it will chunk it!
            self.channel.send_event(
                self.gsock,
                'EV_WRITE_OUTPUT_DATA',
                data=b'0\r\n\r\n'
            )
        if self.close_on_finish:
            self.gsock.close_when_flushed = True
        self.request._close()
        self.channel.send_event(self.gsock, 'EV_FLUSH_OUTPUT_DATA')

    def write(self, data):
        if not self.complete:
            raise RuntimeError('start_response was not called before body '
                               'written')
        gsock = self.gsock
        if not self.wrote_header:
            rh = self.build_response_header()
            self.channel.send_event(gsock, 'EV_WRITE_OUTPUT_DATA', data=rh)
            self.wrote_header = True
        if data:
            towrite = data
            cl = self.content_length
            if self.chunked_response:
                # use chunked encoding response
                towrite = tobytes(hex(len(data))[2:].upper()) + b'\r\n'
                towrite += data + b'\r\n'
            elif cl is not None:
                towrite = data[:cl - self.content_bytes_written]
                self.content_bytes_written += len(towrite)
                if towrite != data and not self.logged_write_excess:
                    logging.error(
                        'application-written content exceeded the number of '
                        'bytes specified by Content-Length header (%s)' % cl)
                    self.logged_write_excess = True
            if towrite:
                self.channel.send_event(
                    gsock,
                    'EV_WRITE_OUTPUT_DATA',
                    data=towrite)


class HttpErrorResponse(HttpResponse):
    """ An error task produces an error response """

    def __init__(self, request):
        HttpResponse.__init__(self, request)
        self.complete = True

    def execute(self):
        e = self.request.error
        body = '%s\r\n\r\n%s' % (e.reason, e.body)
        tag = '\r\n\r\n(generated by ginsfsm)'
        body = body + tag
        self.status = '%s %s' % (e.code, e.reason)
        cl = len(body)
        self.content_length = cl
        self.response_headers.append(('Content-Length', str(cl)))
        self.response_headers.append(('Content-Type', 'text/plain'))
        self.response_headers.append(('Connection', 'close'))
        self.close_on_finish = True
        self.write(tobytes(body))


class HttpSimpleOkResponse(HttpResponse):
    """ An simple OK response """

    def __init__(self, request, body, toclose=True):
        HttpResponse.__init__(self, request)
        self.complete = True
        self.body = body
        self.toclose = toclose

    def execute(self):
        cl = len(self.body)
        self.content_length = cl
        self.response_headers.append(('Content-Length', str(cl)))
        self.response_headers.append(('Content-Type', 'text/plain'))
        if self.toclose:
            self.response_headers.append(('Connection', 'close'))
            self.close_on_finish = True
        self.write(tobytes(self.body))
