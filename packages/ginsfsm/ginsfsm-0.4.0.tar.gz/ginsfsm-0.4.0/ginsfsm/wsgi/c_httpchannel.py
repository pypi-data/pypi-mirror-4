# -*- encoding: utf-8 -*-

from .parser import HTTPRequestParser
from .c_wsgiapp import WSGIApp

from ginsfsm.gobj import GObj


def ac_disconnected(self, event):
    """ httpchannel disconnected, inform to wsgi_server for to drop it.
    """
    self.post_event(self.wsgi_server, 'EV_DISCONNECTED')


def ac_httpchannel_rx_data(self, event):
    """ Received data. Can be one or more requests.
    """
    data = event.data
    if not data:
        return
    new_request = self._current_request
    requests = []
    while data:
        if new_request is None:
            new_request = HTTPRequestParser(
                url_scheme=self.wsgi_server.url_scheme,
                inbuf_overflow=self.inbuf_overflow,
                max_request_header_size=self.max_request_header_size,
                max_request_body_size=self.max_request_body_size)
        n = new_request.received(data)
        if new_request.expect_continue and new_request.headers_finished:
            # guaranteed by parser to be a 1.1 new_request
            new_request.expect_continue = False
            if not self.sent_continue:
                # there's no current task, so we don't need to try to
                # lock the outbuf to append to it.
                self.gsock.outbufs[-1].append(b'HTTP/1.1 100 Continue\r\n\r\n')
                self.sent_expect_continue = True
                self.gsock.send_some()
                new_request.completed = False
        if new_request.completed:
            # The new_request (with the body) is ready to use.
            self._current_request = None
            if not new_request.empty:
                requests.append(new_request)
            new_request = None
        else:
            self._current_request = new_request
        if n >= len(data):
            break
        data = data[n:]

    if requests:
        self.send_event(self.wsgiapp, 'EV_EXECUTE_REQUESTS', requests=requests)


def ac_timeout(self, event):
    #TODO: channel_timeout = 120 inactivity timeout
    pass


HTTPCHANNEL_FSM = {
    'event_list': ('EV_TIMEOUT', 'EV_DISCONNECTED', 'EV_RX_DATA',),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',          ac_timeout,             'ST_IDLE'),
            ('EV_DISCONNECTED',     ac_disconnected,        'ST_IDLE'),
            ('EV_RX_DATA',          ac_httpchannel_rx_data, 'ST_IDLE'),
        ),
    }
}

HTTPCHANNEL_GCONFIG = {
    'wsgi_server': [None, None, 0, None, "wsgi server"],
    'gsock': [None, None, 0, None, "clisrv gsock"],
    # A tempfile should be created if the pending input is larger than
    # inbuf_overflow, which is measured in bytes. The default is 512K.  This
    # is conservative.
    'inbuf_overflow': [int, 524288, 0, None, ""],
    # maximum number of bytes of all request headers combined (256K default)
    'max_request_header_size': [int, 262144, 0, None, ""],
    # maximum number of bytes in request body (1GB default)
    'max_request_body_size': [int, 1073741824, 0, None, ""],
}


class HTTPChannel(GObj):
    """  HTTP Channel gobj.
    """
    def __init__(self):
        GObj.__init__(self, HTTPCHANNEL_FSM, HTTPCHANNEL_GCONFIG)
        self._current_request = None  # current receiving request

    def start_up(self):
        self.gsock.delete_all_subscriptions()
        self.gsock.subscribe_event(None, self)  # take on all gsock events

        if self.name and len(self.name):
            prefix_name = self.name
        else:
            prefix_name = None
        self.wsgiapp = self.create_gobj(
            prefix_name + '.wsgi-app' if prefix_name else None,
            WSGIApp,
            self,
            wsgi_server=self.wsgi_server,
            gsock=self.gsock,
        )
