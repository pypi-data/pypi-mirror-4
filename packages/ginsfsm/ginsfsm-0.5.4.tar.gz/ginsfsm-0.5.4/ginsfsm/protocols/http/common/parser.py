##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""HTTP Request Parser

This server uses asyncore to accept connections and do initial
processing but threads to do work.
"""
import re
from io import BytesIO
import sys

from ginsfsm import __version__
from ginsfsm.buffers import ReadOnlyFileBasedBuffer
from ginsfsm.compat import (
    tostr,
    urlparse,
    unquote_bytes_to_wsgi,
)

from ginsfsm.buffers import OverflowableBuffer

from ginsfsm.protocols.http.common.receiver import (
    FixedStreamReceiver,
    ChunkedReceiver,
)

from ginsfsm.protocols.http.common.utilities import (
    find_double_newline,
    RequestEntityTooLarge,
    RequestHeaderFieldsTooLarge,
)

rename_headers = {
    'CONTENT_LENGTH': 'CONTENT_LENGTH',
    'CONTENT_TYPE': 'CONTENT_TYPE',
}


def build_environment(request, server_name, server_port, remote_addr):
    """ Build a wsgi enviroment from a request.
        You need to know the server name/port and the remote addr
    """
    environ = {}
    path = request.path
    while path and path.startswith('/'):
        path = path[1:]

    environ['REQUEST_METHOD'] = request.command.upper()
    environ['SERVER_PORT'] = server_port
    environ['SERVER_NAME'] = server_name
    environ['SERVER_SOFTWARE'] = 'ginsfsm-%s' % __version__
    environ['SERVER_PROTOCOL'] = 'HTTP/%s' % request.version
    environ['SCRIPT_NAME'] = ''
    environ['PATH_INFO'] = '/' + path
    environ['QUERY_STRING'] = request.query
    environ['REMOTE_ADDR'] = remote_addr

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
    return environ


class HTTPRequestParser(object):
    """A structure that collects the HTTP request.
    """
    # Other attributes: first_line, header, headers, command, uri, version,
    # path, query, fragment

    def __init__(self, channel=None):
        # headers is a mapping containing keys translated to uppercase
        # with dashes turned into underscores.
        self.channel = None
        self.url_scheme = 'http'
        self.inbuf_overflow = 524288
        self.max_request_header_size = 262144
        self.max_request_body_size = 1073741824
        if channel:
            self.channel = channel
            self.url_scheme = channel.config.url_scheme
            self.inbuf_overflow = channel.config.inbuf_overflow
            self.max_request_header_size = \
                channel.config.max_request_header_size
            self.max_request_body_size = channel.config.max_request_body_size

        self.headers = {}

        # these variables were in the class section
        self.completed = False  # Set once request is completed.
        self.empty = False        # Set if no request was made.
        self.expect_continue = False  # client sent "Expect: 100-continue" hder
        self.headers_finished = False  # True when headers have been read
        self.header_plus = b''
        self.chunked = False
        self.content_length = 0
        self.header_bytes_received = 0
        self.body_bytes_received = 0
        self.body_rcv = None
        self.version = '1.0'
        self.error = None
        self.connection_close = False

    def received(self, data):
        """
        Receives the HTTP stream for one request.  Returns the number of
        bytes consumed.  Sets the completed flag once both the header and the
        body have been received.
        """
        if self.completed:
            return 0  # Can't consume any more.
        datalen = len(data)
        br = self.body_rcv
        if br is None:
            # In header.
            s = self.header_plus + data
            index = find_double_newline(s)
            if index >= 0:
                # Header finished.
                header_plus = s[:index]
                consumed = len(data) - (len(s) - index)
                # Remove preceeding blank lines.
                header_plus = header_plus.lstrip()
                if not header_plus:
                    self.empty = True
                    self.completed = True
                else:
                    self.parse_header(header_plus)
                    if self.body_rcv is None:
                        # no content-length header and not a t-e: chunked
                        # request
                        self.completed = True
                    if self.content_length > 0:
                        max_body = self.max_request_body_size
                        # we won't accept this request if the content-length
                        # is too large
                        if self.content_length >= max_body:
                            self.error = RequestEntityTooLarge(
                                'exceeds max_body of %s' % max_body)
                            self.completed = True
                self.headers_finished = True
                return consumed
            else:
                # Header not finished yet.
                self.header_bytes_received += datalen
                max_header = self.max_request_header_size
                if self.header_bytes_received >= max_header:
                    self.parse_header(b'GET / HTTP/1.0\n')
                    self.error = RequestHeaderFieldsTooLarge(
                        'exceeds max_header of %s' % max_header)
                    self.completed = True
                self.header_plus = s
                return datalen
        else:
            # In body.
            consumed = br.received(data)
            self.body_bytes_received += consumed
            max_body = self.max_request_body_size
            if self.body_bytes_received >= max_body:
                # this will only be raised during t-e: chunked requests
                self.error = RequestEntityTooLarge(
                    'exceeds max_body of %s' % max_body)
                self.completed = True
            elif br.error:
                # garbage in chunked encoding input probably
                self.error = br.error
                self.completed = True
            elif br.completed:
                self.completed = True
            return consumed

    def parse_header(self, header_plus):
        """
        Parses the header_plus block of text (the headers plus the
        first line of the request).
        """
        index = header_plus.find(b'\n')
        if index >= 0:
            first_line = header_plus[:index].rstrip()
            header = header_plus[index + 1:]
        else:
            first_line = header_plus.rstrip()
            header = b''

        self.first_line = first_line  # for testing

        lines = get_header_lines(header)

        headers = self.headers
        for line in lines:
            index = line.find(b':')
            if index > 0:
                key = line[:index]
                value = line[index + 1:].strip()
                key1 = tostr(key.upper().replace(b'-', b'_'))
                # If a header already exists, we append subsequent values
                # seperated by a comma. Applications already need to handle
                # the comma seperated values, as HTTP front ends might do
                # the concatenation for you (behavior specified in RFC2616).
                try:
                    headers[key1] += tostr(b', ' + value)
                except KeyError:
                    headers[key1] = tostr(value)
            # else there's garbage in the headers?

        # command, uri, version will be bytes
        command, uri, version = crack_request_first_line(first_line)
        version = tostr(version)
        command = tostr(command)
        self.command = self.method = command
        self.version = version
        (self.proxy_scheme,
         self.proxy_netloc,
         self.path,
         self.query, self.fragment) = split_uri(uri)
        self.url_scheme = self.url_scheme
        connection = headers.get('CONNECTION', '')

        if version == '1.0':
            if connection.lower() != 'keep-alive':
                self.connection_close = True

        if version == '1.1':
            te = headers.get('TRANSFER_ENCODING', '')
            if te == 'chunked':
                self.chunked = True
                buf = OverflowableBuffer(self.inbuf_overflow)
                self.body_rcv = ChunkedReceiver(buf)
            expect = headers.get('EXPECT', '').lower()
            self.expect_continue = expect == '100-continue'
            if connection.lower() == 'close':
                self.connection_close = True

        if not self.chunked:
            try:
                cl = int(headers.get('CONTENT_LENGTH', 0))
            except ValueError:
                cl = 0
            self.content_length = cl
            if cl > 0:
                buf = OverflowableBuffer(self.inbuf_overflow)
                self.body_rcv = FixedStreamReceiver(cl, buf)

    def get_body_stream(self):
        body_rcv = self.body_rcv
        if body_rcv is not None:
            return body_rcv.getfile()
        else:
            return BytesIO()

    def _close(self):
        body_rcv = self.body_rcv
        if body_rcv is not None:
            body_rcv.getbuf()._close()


class HTTPResponseParser(object):
    """A structure that collects the HTTP response.
    """
    # Other attributes: first_line, header, headers, command, uri, version,
    # path, query, fragment

    def __init__(self, channel=None):
        # headers is a mapping containing keys translated to uppercase
        # with dashes turned into underscores.
        self.channel = None
        self.url_scheme = 'http'
        self.inbuf_overflow = 524288
        self.max_request_header_size = 262144
        self.max_request_body_size = 1073741824
        if channel:
            self.channel = channel
            self.url_scheme = channel.config.url_scheme
            self.inbuf_overflow = channel.config.inbuf_overflow
            self.max_request_header_size = \
                channel.config.max_request_header_size
            self.max_request_body_size = channel.config.max_request_body_size

        self.headers = {}

        # these variables were in the class section
        self.completed = False  # Set once request is completed.
        self.empty = False        # Set if no request was made.
        self.expect_continue = False  # client sent "Expect: 100-continue" hder
        self.headers_finished = False  # True when headers have been read
        self.header_plus = b''
        self.chunked = False
        self.content_length = 0
        self.header_bytes_received = 0
        self.body_bytes_received = 0
        self.body_rcv = None
        self.version = '1.0'
        self.error = None
        self.connection_close = False

    def received(self, data):
        """
        Receives the HTTP stream for one request.  Returns the number of
        bytes consumed.  Sets the completed flag once both the header and the
        body have been received.
        """
        if self.completed:
            return 0  # Can't consume any more.
        datalen = len(data)
        br = self.body_rcv
        if br is None:
            # In header.
            s = self.header_plus + data
            index = find_double_newline(s)
            if index >= 0:
                # Header finished.
                header_plus = s[:index]
                consumed = len(data) - (len(s) - index)
                # Remove preceeding blank lines.
                header_plus = header_plus.lstrip()
                if not header_plus:
                    self.empty = True
                    self.completed = True
                else:
                    self.parse_header(header_plus)
                    if self.body_rcv is None:
                        # no content-length header and not a t-e: chunked
                        # request
                        self.completed = True
                    if self.content_length > 0:
                        max_body = self.max_request_body_size
                        # we won't accept this request if the content-length
                        # is too large
                        if self.content_length >= max_body:
                            self.error = RequestEntityTooLarge(
                                'exceeds max_body of %s' % max_body)
                            self.completed = True
                self.headers_finished = True
                return consumed
            else:
                # Header not finished yet.
                self.header_bytes_received += datalen
                max_header = self.max_request_header_size
                if self.header_bytes_received >= max_header:
                    self.parse_header(b'GET / HTTP/1.0\n')
                    self.error = RequestHeaderFieldsTooLarge(
                        'exceeds max_header of %s' % max_header)
                    self.completed = True
                self.header_plus = s
                return datalen
        else:
            # In body.
            consumed = br.received(data)
            self.body_bytes_received += consumed
            max_body = self.max_request_body_size
            if self.body_bytes_received >= max_body:
                # this will only be raised during t-e: chunked requests
                self.error = RequestEntityTooLarge(
                    'exceeds max_body of %s' % max_body)
                self.completed = True
            elif br.error:
                # garbage in chunked encoding input probably
                self.error = br.error
                self.completed = True
            elif br.completed:
                self.completed = True
            return consumed

    def parse_header(self, header_plus):
        """
        Parses the header_plus block of text (the headers plus the
        first line of the request).
        """
        index = header_plus.find(b'\n')
        if index >= 0:
            first_line = header_plus[:index].rstrip()
            header = header_plus[index + 1:]
        else:
            first_line = header_plus.rstrip()
            header = b''

        self.first_line = first_line  # for testing

        lines = get_header_lines(header)

        headers = self.headers
        for line in lines:
            index = line.find(b':')
            if index > 0:
                key = line[:index]
                value = line[index + 1:].strip()
                key1 = tostr(key.upper().replace(b'-', b'_'))
                # If a header already exists, we append subsequent values
                # seperated by a comma. Applications already need to handle
                # the comma seperated values, as HTTP front ends might do
                # the concatenation for you (behavior specified in RFC2616).
                try:
                    headers[key1] += tostr(b', ' + value)
                except KeyError:
                    headers[key1] = tostr(value)
            # else there's garbage in the headers?

        # version, status, status_info will be bytes
        version, status, status_info = crack_response_first_line(first_line)
        try:
            status = int(tostr(status))
        except ValueError:
            status = 0

        version = tostr(version)
        status_info = tostr(status_info)
        self.version = version
        self.status = status
        self.status_info = status_info
        self.url_scheme = self.url_scheme
        connection = headers.get('CONNECTION', '')

        if version == '1.0':
            if connection.lower() != 'keep-alive':
                self.connection_close = True

        if version == '1.1':
            te = headers.get('TRANSFER_ENCODING', '')
            if te == 'chunked':
                self.chunked = True
                buf = OverflowableBuffer(self.inbuf_overflow)
                self.body_rcv = ChunkedReceiver(buf)
            expect = headers.get('EXPECT', '').lower()
            self.expect_continue = expect == '100-continue'
            if connection.lower() == 'close':
                self.connection_close = True

        if not self.chunked:
            try:
                cl = int(headers.get('CONTENT_LENGTH', 0))
            except ValueError:
                cl = 0
            self.content_length = cl
            if cl > 0:
                buf = OverflowableBuffer(self.inbuf_overflow)
                self.body_rcv = FixedStreamReceiver(cl, buf)

    def get_body_stream(self):
        body_rcv = self.body_rcv
        if body_rcv is not None:
            return body_rcv.getfile()
        else:
            return BytesIO()

    def _close(self):
        body_rcv = self.body_rcv
        if body_rcv is not None:
            body_rcv.getbuf()._close()


def split_uri(uri):
    # urlsplit handles byte input by returning bytes on py3, so
    # scheme, netloc, path, query, and fragment are bytes
    scheme, netloc, path, query, fragment = urlparse.urlsplit(uri)
    return (
        tostr(scheme),
        tostr(netloc),
        unquote_bytes_to_wsgi(path),
        tostr(query),
        tostr(fragment),
    )


def get_header_lines(header):
    """
    Splits the header into lines, putting multi-line headers together.
    """
    r = []
    lines = header.split(b'\n')
    for line in lines:
        if line.startswith((b' ', b'\t')):
            r[-1] = r[-1] + line[1:]
        else:
            r.append(line)
    return r


request_first_line_re = re.compile(
b'([^ ]+) ((?:[^ :?#]+://[^ ?#/]*(?:[0-9]{1,5})?)?[^ ]+)(( HTTP/([0-9.]+))$|$)')


def crack_request_first_line(line):
    m = request_first_line_re.match(line)
    if m is not None and m.end() == len(line):
        if m.group(3):
            version = m.group(5)
        else:
            version = None
        command = m.group(1).upper()
        uri = m.group(2)
        return command, uri, version
    else:
        return b'', b'', b''


response_first_line_re = re.compile(b'HTTP/(1.[01]) ([0-9]+) (.*)')


def crack_response_first_line(line):
    m = response_first_line_re.match(line)

    if m is not None and m.end() == len(line):
        version = m.group(1)
        status = m.group(2)
        status_info = m.group(3)
        return version, status, status_info
    else:
        return b'', b'', b''
