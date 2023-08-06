"""
GObj :class:`SimpleHttpServer`
==============================

Http serve sample.

The server echo the data.

It uses :class:`ginsfsm.protocols.http.server.c_http_server.GHttpServer`.

.. autoclass:: SimpleHttpServer
    :members:

"""

import logging
logging.basicConfig(level=logging.DEBUG)

from ginsfsm.gaplic import GAplic
from ginsfsm.smachine import SMachine
from ginsfsm.c_sock import GSock
from ginsfsm.gobj import GObj
from ginsfsm.protocols.http.server.c_http_server import GHttpServer
from ginsfsm.protocols.http.common.response import HttpSimpleOkResponse


def ac_channel_opened(self, event):
    print "======> channel opened"


def ac_channel_closed(self, event):
    print "======> channel closed"


def ac_request(self, event):
    print "======> channel request"
    channel = event.source[-1]
    request = event.request
    response = HttpSimpleOkResponse(
        request,
        'Caraculo\r\nCaraculo\r\nCaraculo\r\n'
    )
    self.send_event(channel, 'EV_HTTP_RESPONSE', response=response)


HTTP_ECHO_FSM = {
    'event_list': (
        'EV_HTTP_CHANNEL_OPENED: bottom input',
        'EV_HTTP_CHANNEL_CLOSED: bottom input',
        'EV_HTTP_REQUEST: bottom input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_HTTP_CHANNEL_OPENED',  ac_channel_opened,  'ST_IDLE'),
            ('EV_HTTP_CHANNEL_CLOSED',  ac_channel_closed,  'ST_IDLE'),
            ('EV_HTTP_REQUEST',         ac_request,         'ST_IDLE'),
        ),
    }
}


HTTP_ECHO_GCONFIG = {  # type, default_value, flag, validate_function, desc
    'verbose': [int, 1, 0, None, "Increase output verbosity. Values [0,1,2]"],
}


class SimpleHttpServer(GObj):
    """  Server GObj.

    .. ginsfsm::
       :fsm: HTTP_ECHO_FSM
       :gconfig: HTTP_ECHO_GCONFIG

    *Input-Events:*


    *Output-Events:*


    """
    def __init__(self):
        GObj.__init__(self, HTTP_ECHO_FSM, HTTP_ECHO_GCONFIG)

    def start_up(self):
        self.server = self.create_gobj(
            None,
            GHttpServer,
            self,
            host='0.0.0.0',
            port=8000,
            subscriber=self,
            inactivity_timeout=10,
            responseless_timeout=2,
            maximum_simultaneous_requests=0,
        )

        if self.verbose > 0:
            settings = {
                'GObj.trace_mach': True,
                'GObj.logger': logging,
            }
            self.overwrite_parameters(-1, **settings)
            SMachine._global_trace_mach = True
            GSock._global_trace_dump = True


#===============================================================
#                   Main
#===============================================================
if __name__ == "__main__":
    ga_srv = GAplic('Server')
    ga_srv.create_gobj(
        'server',
        SimpleHttpServer,
        None,
    )

    try:
        ga_srv.mt_process()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')
