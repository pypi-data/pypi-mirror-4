# -*- encoding: utf-8 -*-
""" GStdin GObj

.. autoclass:: GStdin
    :members: start_up

"""

import sys
import fcntl
import os
from ginsfsm.gobj import GObj
from ginsfsm.c_sock import GSock


def ac_rx_data(self, event):
    data = event.kw.get('data', None)
    for c in data:
        if c == self.config.eol:
            line = ''.join(self.buffer)
            self.buffer = []
            self.broadcast_event('EV_RX_DATA', data=line)
        else:
            self.buffer.append(c)


GSTDIN_FSM = {
    'event_list': (
        'EV_RX_DATA:bottom input:top output',
    ),
    'state_list': (
        'ST_IDLE',
    ),
    'machine': {
        'ST_IDLE':
        (
            ('EV_RX_DATA',      ac_rx_data,     'ST_IDLE'),
        ),
    }
}

GSTDIN_GCONFIG = {
    'eol': [
        str, '\n', 0, None,
        "Caracter defining end of line. LF default"
    ],
    'subscriber': [
        None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
    ],
}


class GStdin(GObj):
    """  GStdin GObj.
    Asynchronous stdin. Use stdin as gsock.

    .. ginsfsm::
       :fsm: GSTDIN_FSM
       :gconfig: GSTDIN_GCONFIG

    *Input-Events:*

        * :attr:`'EV_RX_DATA'`: Receiving data.
            Receiving data from stdin.
            Save the data,
            and broadcast when the line is complete (EOL received).

    *Output-Events:*


    """
    def __init__(self):
        GObj.__init__(self, GSTDIN_FSM, GSTDIN_GCONFIG)
        self.buffer = []

    def start_up(self):
        """ Initialization zone.
        """
        if self.config.subscriber is None:
            self.config.subscriber = self.parent
        self.subscribe_event(None, self.config.subscriber)

        gsock = self.gsock = self.create_gobj(
            None,
            GSock,
            self,
            transmit_ready_event_name=None,
            connected_event_name=None,
            disconnected_event_name=None,
        )

        # make stdin a non-blocking file
        fd = sys.stdin.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        gsock.set_clisrv_socket(sys.stdin)
