# -*- coding: utf-8 -*-
"""
    Xhr implementation
"""
import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPServerError

from ginsfsm.gobj import GObj
from ginsfsm.gconfig import GConfig
from ginsfsm.protocols.sockjs.server import proto
from ginsfsm.protocols.sockjs.server.basehandler import SessionHandler
from ginsfsm.protocols.sockjs.server.util import bytes_to_str

#----------------------------------------------------------------#
#                   GXhrSend GClass
#                   /xhr_send
#----------------------------------------------------------------#
GXHRSEND_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GXhrSend(GObj):
    """  GXhr GObj.
    """
    def __init__(self):
        GObj.__init__(self, {}, GXHRSEND_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """


#----------------------------------------------------------------#
#                   GXhrSend Views
#                   /xhr_send
#----------------------------------------------------------------#
@view_config(
    context=GXhrSend,
    name='',
    attr='options',
    request_method='OPTIONS',
)
@view_config(
    context=GXhrSend,
    name='',
    attr='post',
    request_method='POST',
)
class XhrSendHandler(SessionHandler):
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

        data = self.request.body_file.read()
        if not data:
            logging.error('ERROR xhr_send: Payload expected.')
            return HTTPServerError("Payload expected.")

        try:
            messages = proto.json_decode(bytes_to_str(data))  # ? v1.0.0
        except Exception:
            logging.exception(
                'ERROR xhr_send: Invalid json encoding',
            )
            return HTTPServerError("Broken JSON encoding.")

        try:
            session.on_messages(messages)
        except Exception:
            logging.exception(
                'ERROR xhr_send: on_message() failed',
            )
            return HTTPServerError('ERROR xhr_send: on_message() failed')

        self.set_status(204)
        self.response.content_type = 'text/plain'
        self.response.charset = 'UTF-8'
        return response


#----------------------------------------------------------------#
#                   GXhrPolling GClass
#                   /xhr
#----------------------------------------------------------------#
GXHRPOLLING_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GXhrPolling(GObj):
    """  GXhrPolling GObj.
    """
    def __init__(self):
        GObj.__init__(self, {}, GXHRPOLLING_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """


#----------------------------------------------------------------#
#                   GXhrPolling Views
#                   /xhr
#----------------------------------------------------------------#
@view_config(
    context=GXhrPolling,
    name='',
    attr='options',
    request_method='OPTIONS',
)
@view_config(
    context=GXhrPolling,
    name='',
    attr='post',
    request_method='POST',
)
class XhrPollingTransport(SessionHandler):
    """xhr-polling transport implementation"""
    name = 'xhr'

    def __init__(self, context, request):
        super(XhrPollingTransport, self).__init__(
            context,
            request,
            False
        )
        self.session = None
        self.active = True

    def post(self):
        response = self.response

        # Start response
        self.preflight()
        self.handle_session_cookie()
        self.disable_cache()

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
            raise Exception('binary not supported for XhrPollingTransport')

        if not self.active:
            return
        self.active = False

        try:
            self.response.content_type = 'application/javascript'
            self.response.charset = 'UTF-8'

            self.write(message + '\n')
            self.flush()
            self.send_complete()
        except Exception:
            # If connection dropped, make sure we close offending session
            # instead of propagating error all way up.
            logging.exception("ERROR XhrPollingTransport send_pack")
            if self.session:
                self.session.delayed_close()

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


#----------------------------------------------------------------#
#                   GXhrStreaming GClass
#                   /xhr_streaming
#----------------------------------------------------------------#
GXHRSTREAMING_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GXhrStreaming(GObj):
    """  GStreaming GObj.
    """
    def __init__(self):
        GObj.__init__(self, {}, GXHRSTREAMING_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """


#----------------------------------------------------------------#
#                   GXhrStreaming Views
#                   /xhr_streaming
#----------------------------------------------------------------#
@view_config(
    context=GXhrStreaming,
    name='',
    attr='options',
    request_method='OPTIONS',
)
@view_config(
    context=GXhrStreaming,
    name='',
    attr='post',
    request_method='POST',
)
class XhrStreamingTransport(SessionHandler):
    name = 'xhr_streaming'

    def __init__(self, context, request):
        super(XhrStreamingTransport, self).__init__(
            context,
            request,
            True  # Asynchronous response!
        )
        self.session = None
        self.active = True
        self.amount_limit = self.context.sockjs_server.config.response_limit

    def post(self):
        response = self.response

        session_id = self.sid = self.context.parent.re_matched_name

        # Start response
        self.preflight()
        self.handle_session_cookie()
        self.disable_cache()

        response.content_type = 'application/javascript'
        response.charset = 'UTF-8'
        response.write('h' * 2048 + '\n')

        # Get or create session without starting heartbeat
        session = self.context.sockjs_server.get_session(session_id)
        if session is None:
            session = self.context.sockjs_server.create_session(session_id)
        if session is None:
            # close the session in the next cycle.
            self.context.gaplic.add_callback(self.session_closed)
            return response  # how inform of the error? headers has been sent.

        # Try to attach to the session
        if not session.set_handler(self, False):
            # close the session in the next cycle.
            self.context.gaplic.add_callback(self.session_closed)
            return response  # how inform of the error? headers has been sent.
        self.session = session
        # Verify if session is properly opened
        session.verify_state()
        session.flush()

        return response

    def send_pack(self, message, binary=False):
        if binary:
            raise Exception('binary not supported for XhrStreamingTransport')

        #self.active = False  # TODO si chequeo active fallan los tests

        try:
            self.notify_sent(len(message))
            self.write(message + '\n')
            self.flush(callback=self.send_complete)
        except Exception:
            # If connection dropped, make sure we close offending session
            # instead of propagating error all way up.
            if self.session:  # detach session
                self.session.delayed_close()
                self.session.remove_handler(self)
                self.session = None
            logging.exception("ERROR XhrStreamingTransport send_pack")

    def send_complete(self):
        """
            Verify if connection should be closed based on amount of data
            that was sent.
        """
        self.active = True

        if self.should_finish():
            if self.session:  # detach session
                self.session.remove_handler(self)
                self.session = None
            self.context.gaplic.add_callback(self.safe_finish)
        else:
            if self.session:
                self.session.flush()

    def notify_sent(self, data_len):
        """
            Update amount of data sent
        """
        self.amount_limit -= data_len

    def should_finish(self):
        """
            Check if transport should close long running connection after
            sending X bytes to the client.

            `data_len`
                Amount of data that was sent
        """
        if self.amount_limit <= 0:
            return True

        return False

    def session_closed(self):
        """Called by the session when it was closed"""
        if self.session:  # detach session
            self.session.remove_handler(self)
            self.session = None
        self.context.gaplic.add_callback(self.safe_finish)
