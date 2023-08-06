# -*- encoding: utf-8 -*-
"""
GObj :class:`GHttpCliSrv`
=========================

Http Channel.

.. autoclass:: GHttpCliSrv
    :members:

"""
from collections import deque
import traceback

from ginsfsm.c_timer import GTimer
from ginsfsm.gobj import GObj
from ginsfsm.gconfig import GConfig
from ginsfsm.protocols.http.common.parser import HTTPRequestParser
from ginsfsm.protocols.http.common.utilities import InternalServerError
from ginsfsm.protocols.http.common.response import (
    HttpResponse,
    HttpErrorResponse,
)


class ResponseInterrupt(Exception):
    """ To use when the response is asynchronous
        or infinite until top level wants to finish it.
    """


def ac_rx_data(self, event):
    """ Receiving data from the partner clisrv gsock.
        Can be one or more requests.
    """
    self.start_inactivity_timer()
    #gsock = event.source[-1]
    gsock = self.gsock  # must be same as event.source[-1]
    data = event.data
    if not data:
        return
    new_request = self.parsing_request
    while data:
        if new_request is None:
            new_request = HTTPRequestParser(self)
        n = new_request.received(data)
        if new_request.expect_continue and new_request.headers_finished:
            # guaranteed by parser to be a 1.1 new_request
            new_request.expect_continue = False

            if not self.sent_continue:
                self.send_event(
                    gsock,
                    'EV_SEND_DATA',
                    data=b'HTTP/1.1 100 Continue\r\n\r\n'
                )
                self.sent_continue = True
                new_request.completed = False

        if new_request.completed:
            # The new_request (with the body) is ready to use.
            self.parsing_request = None
            if not new_request.empty:
                self.enqueue_request(new_request)
            new_request = None
        else:
            self.parsing_request = new_request
        if n >= len(data):
            break
        data = data[n:]

    if len(self.dl_requests):
        self.send_event(self, 'EV_DEQUEUE_REQUEST')


def ac_dequeue_request(self, event):
    if self.responding_request:
        self.logger.exception('Internal ERROR!!!: '
                              'responding_request MUST be None')
    if len(self.dl_requests):
        self.responding_request = self.dl_requests.popleft()
        self.send_event(self, 'EV_HTTP_REQUEST')
    else:
        self.start_inactivity_timer()


def ac_http_request(self, event):
    """ Internal event.
        The request is saved in self.responding_request.
    """
    self.stop_inactivity_timer()

    if self.responding_request.error:
        response = HttpErrorResponse(self.responding_request)
        response.execute()
        self.finish(response)
        return

    self.start_responseless_timer()
    self.set_new_state('ST_WAIT_RESPONSE')
    # TODO: in stratus environment, we need to inform of who srvcli is.
    self.broadcast_event(
        'EV_HTTP_REQUEST',
        request=self.responding_request,
        channel=self,
    )


def ac_http_response(self, event):
    response = event.response
    if not isinstance(response, HttpResponse):
        self.logger and self.logger.error(
            "ERROR response doesn't mach HttpResponse %s" %
            response.request.path)

    if response.request != self.responding_request:
        self.logger and self.logger.error(
            "ERROR response doesn't mach responding request %s" %
            response.request.path)

    if self.responding_response:
        self.logger and self.logger.error(
            "ERROR responding_response is BUSY, of %s" %
            response.request.path)
    self.responding_response = response

    response.start()
    try:
        response.execute()
    except ResponseInterrupt:
        """ Response is asynchronous or infinite.
            Don't clear the current responding_request.
        """
        self.stop_responseless_timer()  # TODO: do some ping-alive
        return

    except:
        self.logger and self.logger.exception(
            'Exception when serving %s' % response.request.path)
        if not response.wrote_header:
            if self.parent.config.expose_tracebacks:
                body = traceback.format_exc()
            else:
                body = ('The server encountered an unexpected '
                        'internal server error')

            request = HTTPRequestParser(self)
            request.error = InternalServerError(body)
            response = HttpErrorResponse(request)
            response.execute()
        else:
            response.close_on_finish = True

    self.finish(response)


def ac_transmit_ready(self, event):
    pass


def ac_inactivity_timeout(self, event):
    """ Close the channel by inactivity.
    """
    if self.gsock:
        self.send_event(self.gsock, 'EV_DROP')


def ac_responseless_timeout(self, event):
    """ Close the channel by responseless of top level.
    """
    if not self.gsock:
        return

    body = (
        'Response Timeout. The server is busy. '
        'Please re-try your request in a few moments.'
    )
    request = HTTPRequestParser(self)
    request.error = InternalServerError(body)
    response = HttpErrorResponse(request)
    response.execute()
    self.finish(response)


def ac_disconnected(self, event):
    """ Gsock closed.
    """
    self.broadcast_event('EV_HTTP_CHANNEL_CLOSED', channel=self)


GHTTPCLISRV_FSM = {
    'event_list': (
        'EV_SET_TIMER: bottom output',
        'EV_RESPONSELESS_TIMEOUT: bottom input',
        'EV_INACTIVITY_TIMEOUT: bottom input',
        'EV_DISCONNECTED: bottom input',
        'EV_RX_DATA: bottom input',
        'EV_DEQUEUE_REQUEST',
        'EV_TRANSMIT_READY: bottom input',
        'EV_SEND_DATA: bottom output',
        'EV_FLUSH_OUTPUT_DATA: bottom output',
        'EV_WRITE_OUTPUT_DATA: bottom output',
        'EV_HTTP_CHANNEL_OPENED: top output',
        'EV_HTTP_CHANNEL_CLOSED: top output',
        'EV_HTTP_REQUEST: top output',
        'EV_HTTP_RESPONSE: top input',
    ),
    'state_list': (
        'ST_IDLE',
        'ST_WAIT_RESPONSE',
    ),
    'machine': {
        'ST_IDLE':
        (
            ('EV_DISCONNECTED',         ac_disconnected,            None),
            ('EV_INACTIVITY_TIMEOUT',   ac_inactivity_timeout,      None),
            ('EV_RX_DATA',              ac_rx_data,                 None),
            ('EV_DEQUEUE_REQUEST',      ac_dequeue_request,         None),
            ('EV_HTTP_REQUEST',         ac_http_request,            None),
        ),
        'ST_WAIT_RESPONSE':
        (
            ('EV_DISCONNECTED',         ac_disconnected,            None),
            ('EV_RESPONSELESS_TIMEOUT', ac_responseless_timeout,    'ST_IDLE'),
            ('EV_RX_DATA',              ac_rx_data,                 None),
            ('EV_DEQUEUE_REQUEST',      None,                       None),
            ('EV_HTTP_RESPONSE',        ac_http_response,           'ST_IDLE'),

            ('EV_TRANSMIT_READY',       ac_transmit_ready,          None),
        ),
    }
}

GHTTPCLISRV_GCONFIG = {
    'subscriber': [
        None, None, 0, None,
        "subcriber of all output-events."
    ],
    'gsock': [
        None, None, GConfig.FLAG_DIRECT_ATTR, None, "partner gsock."
    ],
    'maximum_simultaneous_requests': [
        int, 0, 0, None,
        "maximum simultaneous requests."
    ],
    'inactivity_timeout': [
        int, 5 * 60 * 60, 0, None,
        "Inactivity timeout in seconds."
    ],
    'responseless_timeout': [
        int, 5 * 60 * 60, 0, None,
        "'Without response' timeout in seconds."
    ],

    # Used in parser:
    'url_scheme': [str, 'http', 0, None, "default ``http`` value"],
    # A tempfile should be created if the pending input is larger than
    # inbuf_overflow, which is measured in bytes. The default is 512K.  This
    # is conservative.
    'inbuf_overflow': [int, 524288, 0, None, ""],
    # maximum number of bytes of all request headers combined (256K default)
    'max_request_header_size': [int, 262144, 0, None, ""],
    # maximum number of bytes in request body (1GB default)
    'max_request_body_size': [int, 1073741824, 0, None, ""],
}


class GHttpCliSrv(GObj):
    """  Http clisrv (client of server) class.

    This gobj is create by GHttpServer when it receives an EV_CONNECTED event
    from a new gsock gobj.

    This class will subscribe all the events of the partner
    :class:`ginsfsm.c_sock.GSock` gobj, to implement the http protocol.

    .. ginsfsm::
       :fsm: GHTTPCLISRV_FSM
       :gconfig: GHTTPCLISRV_GCONFIG

    *Top Output-Events:*
        * :attr:`'EV_HTTP_CHANNEL_OPENED'`: new http client.

          Event attributes:

            * ``channel``: http channel.

        * :attr:`'EV_HTTP_CHANNEL_CLOSED'`: http client closed.

          Event attributes:

            * ``channel``: http channel.

        * :attr:`'EV_HTTP_REQUEST'`: new http request.

          Event attributes:

            * ``channel``: http channel.
            * ``request``: http request.

    *Top Input-Events:*
        * :attr:`'EV_HTTP_RESPONSE'`: response to the current request.

          Event attributes:

            * ``response``: http response.

    *Bottom Input-Events:*
        * :attr:`'EV_DISCONNECTED'`: socket disconnected.

          The clisrv `gobj` will be destroyed.

        * :attr:`'EV_TRANSMIT_READY'`: socket ready to transmit more data.

        * :attr:`'EV_RX_DATA'`: data received. Process http protocol.

    *Bottom Output-Events:*

        * :attr:`'EV_SEND_DATA'`: transmit data socket.
        * :attr:`'EV_WRITE_OUTPUT_DATA'`: write data to socket output buffer.
        * :attr:`'EV_FLUSH_OUTPUT_DATA'`: flush data of socket output buffer.

    """

    def __init__(self):
        GObj.__init__(self, GHTTPCLISRV_FSM, GHTTPCLISRV_GCONFIG)
        self.parsing_request = None  # A request parser instance
        self.responding_request = None  # request waiting a top response
        self.responding_response = None  # current response being responding
        self.dl_requests = deque()  # requests queue
        self.sent_continue = False  # used as a latch after sending 100continue

    def go_out(self):
        """ Finish zone.
        """

    def start_up(self):
        if self.config.subscriber is None:
            self.config.subscriber = self.parent

        # gsock MUST be passed at creating gobj

        # Canalize the flow of messages
        # bottom events for me
        self.gsock.subscribe_event(None, self)

        # we need to know disconnected event for deleting gobjs
        self.gsock.subscribe_event(
            'EV_DISCONNECTED',
            self,
            __hard_subscription__=True,
        )

        # top events for subscriber
        self.subscribe_event(None, self.config.subscriber)
        self.broadcast_event('EV_HTTP_CHANNEL_OPENED', channel=self)

        # Setup the timers
        self.inactivity_timer = self.create_gobj(
            None,
            GTimer,
            self,
            timeout_event_name='EV_INACTIVITY_TIMEOUT'
        )
        self.start_inactivity_timer()

        self.responseless_timer = self.create_gobj(
            None,
            GTimer,
            self,
            timeout_event_name='EV_RESPONSELESS_TIMEOUT'
        )

    def enqueue_request(self, new_request):
        self.dl_requests.append(new_request)
        max_req = self.config.maximum_simultaneous_requests
        if max_req > 0 and len(self.dl_requests) > max_req:
            # Close the channel by maximum simultaneous requests reached.
            body = 'Please change your behavior.' \
                ' You have reached the maximum simultaneous requests (%d).' % (
                    max_req)
            request = HTTPRequestParser(self)
            request.error = InternalServerError(body)
            response = HttpErrorResponse(request)
            response.service()
            self.clear_request_queue()

    def clear_request_queue(self):
        for request in self.dl_requests:
            request._close()
        self.dl_requests.clear()

    def start_inactivity_timer(self):
        self.send_event(
            self.inactivity_timer,
            'EV_SET_TIMER',
            seconds=self.config.inactivity_timeout
        )

    def stop_inactivity_timer(self):
        self.send_event(
            self.inactivity_timer,
            'EV_SET_TIMER',
            seconds=-1
        )

    def start_responseless_timer(self):
        self.send_event(
            self.responseless_timer,
            'EV_SET_TIMER',
            seconds=self.config.responseless_timeout
        )

    def stop_responseless_timer(self):
        self.send_event(
            self.responseless_timer,
            'EV_SET_TIMER',
            seconds=-1
        )

    def write(self, data):
        """ Write data to output buffer.
            To supply asynchronous access to high level.
        """
        if not self.responding_response:
            self.logger and self.logger.error(
                "ERROR channel.write() with no responding_response")
            return
        self.responding_response.write(data)

    def flush(self, callback=None):
        """ Flush output buffer.
            To supply asynchronous access to high level.
        """
        if not self.responding_response:
            self.logger and self.logger.error(
                "ERROR channel.flush() with no responding_response")
            return
        self.responding_response.flush(callback)

    def finish(self, response=None):
        """ Finishes this response,
            flushing output buffer,
            and ending the HTTP request.
            To supply asynchronous access to high level.
        """
        if response is None:
            if not self.responding_response:
                self.logger and self.logger.error(
                    "ERROR channel.finish()"
                    " with no responding_response")
                return
            response = self.responding_response
        response.finish()
        self.stop_responseless_timer()
        self.responding_request = None
        self.responding_response = None

        if response.close_on_finish:
            # ignore all enqueued requests.
            self.clear_request_queue()
            if self.gsock:
                self.gsock.mt_drop()
            return

        # pull the request queue
        self.post_event(self, 'EV_DEQUEUE_REQUEST')
