# -*- coding: utf-8 -*-
"""
    JSONP transport implementation.
"""
import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPServerError

from ginsfsm.gobj import GObj
from ginsfsm.gconfig import GConfig
from ginsfsm.compat import url_unquote_plus
from ginsfsm.protocols.sockjs.server import proto
from ginsfsm.protocols.sockjs.server.basehandler import SessionHandler
from ginsfsm.protocols.sockjs.server.util import bytes_to_str

#----------------------------------------------------------------#
#                   GJsonpSend GClass
#                   /jsonp_send
#----------------------------------------------------------------#
GJSONPSEND_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GJsonpSend(GObj):
    """  GXhr GObj.
    """
    def __init__(self):
        GObj.__init__(self, {}, GJSONPSEND_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """


#----------------------------------------------------------------#
#                   GJsonpSend Views
#                   /jsonp_send
#----------------------------------------------------------------#
@view_config(
    context=GJsonpSend,
    name='',
    attr='options',
    request_method='OPTIONS',
)
@view_config(
    context=GJsonpSend,
    name='',
    attr='post',
    request_method='POST',
)
class JsonpSendHandler(SessionHandler):
    def post(self):
        response = self.response

        # Start response
        self.preflight()
        self.handle_session_cookie()
        self.disable_cache()

        session_id = self.sid = self.context.parent.re_matched_name
        session = self.context.sockjs_server.get_session(session_id)
        if session is None:
            return HTTPNotFound('Session not found')

        data = self.request.body_file.read()  # decode? v1.0.0
        data = bytes_to_str(data)
        ctype = self.request.headers.get('Content-Type', '').lower()
        if ctype == 'application/x-www-form-urlencoded':
            if not data.startswith('d='):
                return HTTPServerError("Payload expected.")

            data = url_unquote_plus(data[2:])

        if not data:
            logging.error('ERROR jsonp_send: Payload expected.')
            return HTTPServerError("Payload expected.")

        try:
            messages = proto.json_decode(data)
        except Exception:
            logging.exception('ERROR jsonp_send: Invalid json encoding')
            return HTTPServerError("Broken JSON encoding.")

        try:
            session.on_messages(messages)
        except Exception:
            logging.exception('ERROR jsonp_send: on_message() failed')
            return HTTPServerError('ERROR jsonp_send: on_message() failed')

        self.set_status(200)
        self.response.content_type = 'text/plain'
        self.response.charset = 'UTF-8'
        self.set_body('ok')
        return response


#----------------------------------------------------------------#
#                   GJsonpPolling GClass
#                   /jsonp
#----------------------------------------------------------------#
GJSONPPOLLING_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GJsonpPolling(GObj):
    """  GJsonpSend GObj.
    """
    def __init__(self):
        GObj.__init__(self, {}, GJSONPPOLLING_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """


#----------------------------------------------------------------#
#                   GJsonpPolling Views
#                   /jsonp
#----------------------------------------------------------------#
@view_config(
    context=GJsonpPolling,
    name='',
    attr='options',
    request_method='OPTIONS',
)
@view_config(
    context=GJsonpPolling,
    name='',
    attr='get',
    request_method='GET',
)
class JsonpPollingTransport(SessionHandler):
    """xhr-polling transport implementation"""
    name = 'jsonp'

    def __init__(self, context, request):
        super(JsonpPollingTransport, self).__init__(
            context,
            request,
            False
        )
        self.session = None
        self.active = True
        self.callback = None

    def get(self):
        response = self.response

        # Start response
        self.handle_session_cookie()
        self.disable_cache()

        # Grab callback parameter
        self.callback = self.request.GET.get('c', None)
        if self.callback is None:
            return HTTPServerError('"callback" parameter required')

        session_id = self.sid = self.context.parent.re_matched_name

        # Get or create session without starting heartbeat
        session = self.context.sockjs_server.get_session(self.sid)
        if session is None:
            session = self.context.sockjs_server.create_session(session_id)
        if session is None:
            return HTTPServerError("ERROR creating session.")

        # Try to attach to the session
        if not session.set_handler(self, False):
            return response
        self.session = session
        # Verify if session is properly opened
        session.verify_state()

        # Might get already detached because connection was closed in on_open
        if not self.session:
            return response

        if not self.session.send_queue:
            self.session.start_heartbeat()
        else:
            self.session.flush()
        return response

    def send_pack(self, message, binary=False):
        if binary:
            raise Exception('binary not supported for JsonpPollingTransport')

        if not self.active:
            return
        self.active = False

        try:
            self.response.content_type = 'application/javascript'
            self.response.charset = 'UTF-8'
            # TODO: Fix me
            self.set_header('Etag', 'dummy')

            # TODO: Just escape
            msg = '%s(%s);\r\n' % (self.callback, proto.json_encode(message))
            self.write(msg)
            self.flush()
            self.send_complete()
        except Exception:
            # If connection dropped, make sure we close offending session
            # instead of propagating error all way up.
            logging.exception(
                "ERROR JsonpPollingTransport send_pack")
            if self.session:
                self.session.delayed_close()
            raise

    def send_complete(self):
        if self.session:  # detach session
            self.session.remove_handler(self)
            self.session = None
        self.active = True

    def session_closed(self):
        """Called by the session when it was closed"""
        if self.session:  # detach session
            self.session.remove_handler(self)
            self.session = None
        self.context.gaplic.add_callback(self.safe_finish)
