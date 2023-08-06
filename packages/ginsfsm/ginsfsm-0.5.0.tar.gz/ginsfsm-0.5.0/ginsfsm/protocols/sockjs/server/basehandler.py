# -*- encoding: utf-8 -*-
""" basehandler
"""

from datetime import datetime, timedelta

from pyramid.response import Response

from ginsfsm.protocols.sockjs.server.session import ConnectionInfo
from ginsfsm.protocols.wsgi.webob.async_response import AsyncResponse
from ginsfsm.deferred import Deferred
from ginsfsm.compat import bytes_

#----------------------------------------------------------------#
#                   Base Views
#----------------------------------------------------------------#
CACHE_TIME = 31536000


class BaseHandler(object):
    def __init__(self, context, request, async_response=False):
        self.context = context
        self.request = request
        self.gsock = request.environ['ginsfsm.gsock']
        self.async_response = async_response
        if async_response:
            self.response = AsyncResponse()
        else:
            self.response = Response()

    # Various helpers
    def set_header(self, name, value):
        """Sets the given response header name and value.
        """
        self.response.headerlist.append((name, value))

    def set_status(self, code):
        self.response.status = code

    def set_body(self, body):
        if self.async_response:
            pass  # be care writing to body in async mode
        self.response.body = bytes_(body, "utf-8")

    def enable_cache(self):
        """Enable client-side caching for the current request"""
        d = datetime.now() + timedelta(seconds=CACHE_TIME)
        self.set_header('Cache-Control', 'max-age=%d, public' % CACHE_TIME)
        self.set_header('Expires', d.strftime('%a, %d %b %Y %H:%M:%S'))
        self.set_header('Access-Control-Max-Age', str(CACHE_TIME))

    def disable_cache(self):
        """Disable client-side cache for the current request"""
        self.set_header(
            'Cache-Control',
            'no-store, no-cache, must-revalidate, max-age=0'
        )

    def handle_session_cookie(self):
        """Handle JSESSIONID cookie logic"""
        # Tornado:
        # If JSESSIONID support is disabled in the settings,
        # ignore cookie logic
        if not self.context.sockjs_server.config.jsessionid:
            return

        cookie = self.request.cookies.get('JSESSIONID')

        if not cookie:
            cookie = 'dummy'

        self.response.set_cookie('JSESSIONID', cookie)
        return ('Set-Cookie', self.response.headers['Set-Cookie'])

    def write(self, data):
        """ Write data.
            It will use the configurated response: async or sync.
        """
        self.response.write(bytes_(data))

    def flush(self, callback=None):
        """Flushes the current output buffer to the network.

        The ``callback`` argument, if given, can be used for flow control:
        it will be run when all flushed data has been written to the socket.
        Note that only one flush callback can be outstanding at a time;
        if another flush occurs before the previous flush's callback
        has been run, the previous callback will be discarded.
        """
        if self.async_response:
            self.response.flush(callback)
        else:
            if callback:
                self.context.gaplic.add_callback(callback)

    def finish(self):
        """Finishes this response, ending the HTTP request."""
        if self.async_response:
            self.response.finish()
        else:
            if self.gsock:
                gsock = self.gsock
                self.gsock = None
                gsock.mt_drop()

    def safe_finish(self):
        """ Finish session. Ignore any error.
        """
        try:
            self.finish()
        except:
            pass

    def get_conn_info(self):
        """Return `ConnectionInfo` object from current transport"""
        return ConnectionInfo(
            self.request.remote_addr,  # remote_ip
            self.request.cookies,
            self.request.params,  # arguments
            self.request.headers,
            self.request.path
        )


class PreflightHandler(BaseHandler):
    """CORS preflight handler"""

    def __init__(self, context, request, async_response=False):
        super(PreflightHandler, self).__init__(
            context, request, async_response
        )

    def options(self, *args, **kwargs):
        """XHR cross-domain OPTIONS handler"""
        # Force a clean sync Response.
        # Several views point here: both async and sync responses.
        response = self.response = Response()

        self.enable_cache()
        self.handle_session_cookie()
        self.preflight()

        if self.verify_origin():
            allowed_methods = getattr(self, 'access_methods', 'OPTIONS, POST')
            self.set_header('Access-Control-Allow-Methods', allowed_methods)
            self.set_header('Allow', allowed_methods)
            self.set_status(204)
        else:
            # Set forbidden
            self.set_status(403)

        return response

    def preflight(self):
        """ Handles request authentication
            Cors headers.
        """
        request = self.request
        # origin = self.request.headers.get('Origin', '*') tornado
        origin = request.environ.get("HTTP_ORIGIN", '*')
        if origin == 'null':
            origin = '*'  # Respond with '*' to 'null' origin

        self.set_header('Access-Control-Allow-Origin', origin)

        # headers = self.request.headers.get('Access-Control-Request-Headers')
        headers = request.environ.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
        if headers:
            self.set_header('Access-Control-Allow-Headers', headers)

        self.set_header('Access-Control-Allow-Credentials', 'true')

    def verify_origin(self):
        """Verify if request can be served"""
        # TODO: Verify origin
        return True


class SessionHandler(PreflightHandler):
    """Session handler"""

    # TODO: pasa todo lo de sessio aquí!

    def __init__(self, context, request, async_response=False):
        super(SessionHandler, self).__init__(
            context, request, async_response
        )
        self.session = None
        deferred = Deferred(0, self.on_connection_close)
        self.gsock.subscribe_event('EV_DISCONNECTED', deferred)

    def on_connection_close(self, event=None):
        # If connection was dropped by the client, close session.
        # In all other cases, connection will be closed by the server.
        if self.session is not None:
            self.session.close(1002, 'Connection interrupted')
