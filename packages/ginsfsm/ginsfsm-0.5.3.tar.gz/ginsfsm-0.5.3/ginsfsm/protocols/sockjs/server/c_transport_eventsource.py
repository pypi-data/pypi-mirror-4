# -*- coding: utf-8 -*-
"""
    EventSource transport implementation.
"""
import logging
from pyramid.view import view_config

from ginsfsm.gobj import GObj
from ginsfsm.gconfig import GConfig
from ginsfsm.protocols.sockjs.server.basehandler import SessionHandler

#----------------------------------------------------------------#
#                   GEventsourceStreaming GClass
#                   /eventsource
#----------------------------------------------------------------#
GEVENTSOURCESTREAMING_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GEventsourceStreaming(GObj):
    """  GEventsourceStreaming GObj.
    """
    def __init__(self):
        GObj.__init__(self, {}, GEVENTSOURCESTREAMING_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """


#----------------------------------------------------------------#
#                   GEventsourceStreaming Views
#                   /eventsource
#----------------------------------------------------------------#
@view_config(
    context=GEventsourceStreaming,
    name='',
    attr='options',
    request_method='OPTIONS',
)
@view_config(
    context=GEventsourceStreaming,
    name='',
    attr='get',
    request_method='GET',
)
class EventsourceStreamingTransport(SessionHandler):
    name = 'eventsource'

    def __init__(self, context, request):
        super(EventsourceStreamingTransport, self).__init__(
            context,
            request,
            True  # Asynchronous response!
        )
        self.session = None
        self.active = True
        self.amount_limit = self.context.sockjs_server.config.response_limit

    def get(self):
        response = self.response

        session_id = self.sid = self.context.parent.re_matched_name

        # Start response
        self.preflight()
        self.handle_session_cookie()
        self.disable_cache()

        response.content_type = 'text/event-stream'
        response.charset = 'UTF-8'
        self.write('\r\n')
        self.flush()

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
            raise Exception(
                'binary not supported for EventsourceStreamingTransport'
            )

        msg = 'data: %s\r\n\r\n' % message

        #self.active = False  # TODO si chequeo active fallan los tests

        try:
            self.notify_sent(len(msg))
            self.write(msg)
            self.flush(callback=self.send_complete)
        except Exception:
            logging.exception(
                "ERROR EventsourceStreamingTransport send_pack")
            # If connection dropped, make sure we close offending session
            # instead of propagating error all way up.
            if self.session:  # detach session
                self.session.delayed_close()
                self.session.remove_handler(self)
                self.session = None

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
