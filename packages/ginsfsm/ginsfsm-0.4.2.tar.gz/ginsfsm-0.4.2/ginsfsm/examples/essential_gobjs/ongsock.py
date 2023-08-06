"""
GObj :class:`OnGSock`
=====================

Utility for check :class:`ginsfsm.c_sock.GSock`.

Connect to an url, get /, and disconnect, periodically.

.. autoclass:: OnGSock
    :members:

"""

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_timer import GTimer
from ginsfsm.c_sock import GSock
from ginsfsm.utils import hexdump

import logging
logging.basicConfig(level=logging.DEBUG)

QUERY = "GET / HTTP/1.1\r\n" + \
    "Host: %s\r\n" + \
    "\r\n"


def ac_connect(self, event):
    self.send_event(self.gsock, 'EV_CONNECT')
    self.set_timeout(60)


def ac_connected(self, event):
    self.clear_timeout()
    self.set_timeout(self.seconds)


def ac_transmit(self, event):
    data = QUERY % self.url
    if self.verbose:
        print('Send %s' % data)
    self.send_event(self.gsock, 'EV_SEND_DATA', data=data)


def ac_disconnect(self, event):
    self.send_event(self.gsock, 'EV_DROP')


def ac_disconnected(self, event):
    self.set_timeout(self.seconds)


def ac_rx_data(self, event):
    data = event.kw['data']
    if self.verbose:
        print('Receiving %d bytes' % len(data))
        print(hexdump('<=', data))


def ac_timeout_connect(self, event):
    self.set_new_state('ST_DISCONNECTED')
    self.set_timeout(5)

ONGSOCK_FSM = {
    'event_list': (
        'EV_SET_TIMER: bottom output',
        'EV_TIMEOUT:bottom input',
        'EV_CONNECTED:bottom input',
        'EV_DISCONNECTED:bottom input',
        'EV_RX_DATA:bottom input',
        'EV_TRANSMIT_READY:bottom input',
    ),
    'state_list': (
        'ST_DISCONNECTED',
        'ST_WAIT_CONNECTED',
        'ST_CONNECTED',
    ),
    'machine': {
        'ST_DISCONNECTED':
        (
            ('EV_TIMEOUT',          ac_connect,         'ST_WAIT_CONNECTED'),
        ),
        'ST_WAIT_CONNECTED':
        (
            ('EV_CONNECTED',        ac_connected,       'ST_CONNECTED'),
            ('EV_DISCONNECTED',     ac_disconnected,    'ST_DISCONNECTED'),
            ('EV_TIMEOUT',          ac_timeout_connect, None),
        ),
        'ST_CONNECTED':
        (
            ('EV_DISCONNECTED',     ac_disconnected,    'ST_DISCONNECTED'),
            ('EV_TIMEOUT',          ac_disconnect,      None),
            ('EV_RX_DATA',          ac_rx_data,         None),
            ('EV_TRANSMIT_READY',   ac_transmit,        None),
        ),
    }
}


ONGSOCK_GCONFIG = {  # type, default_value, flag, validate_function, desc
    'verbose': [int, 0, 0, None, "Increase output verbosity. Values [0,1,2]"],
    'seconds': [int, 5, 0, None, "Seconds to repeat the connection."],
    'url': [str, 'www.google.com', 0, None, "Url to connect."],
}


class OnGSock(GObj):
    """  OnGSock GObj.

    .. ginsfsm::
       :fsm: ONGSOCK_FSM
       :gconfig: ONGSOCK_GCONFIG

    *Input-Events:*

        * :attr:`'EV_TIMEOUT'`: Timer over.
            Start the machine.

        * :attr:`'EV_CONNECTED'`: Connected to url.

        * :attr:`'EV_DISCONNECTED'`: Disconnected from url.

        * :attr:`'EV_RX_DATA'`: Receiving data from url.

        * :attr:`'EV_TRANSMIT_READY'`: Url ready to transmit it data.


    *Output-Events:*

        * :attr:`'EV_START_TIMER'`: Start timer.

    """
    def __init__(self):
        GObj.__init__(self, ONGSOCK_FSM, ONGSOCK_GCONFIG)

    def start_up(self):
        """ Initialization zone."""
        self.timer = self.create_gobj(
            None,
            GTimer,
            self,
            timeout_event_name='EV_TIMEOUT',
        )
        self.timer.subscribe_event('EV_TIMEOUT', self)

        self.gsock = self.create_gobj(
            None,
            GSock,
            self,
            connected_event_name='EV_CONNECTED',
            disconnected_event_name='EV_DISCONNECTED',
            host=self.url,
            port=80,
        )

        if self.verbose > 1:
            settings = {
                'GObj.trace_mach': True,
                'GObj.logger': logging,
            }
            self.overwrite_parameters(-1, **settings)

        self.set_timeout(1)

    def set_timeout(self, seconds):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=seconds)

    def clear_timeout(self):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=-1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "seconds",
        type=int,
        nargs='?', default=2,
        help="Seconds to repeat the url."
    )
    parser.add_argument(
        "url",
        nargs='?', default='www.google.com',
        help="Url to connect."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        type=int,
        choices=[0, 1, 2],
        default=1,
    )
    args = parser.parse_args()

    ga = GAplic()
    ga.create_gobj(
        'ongsock',
        OnGSock,
        None,
        verbose=args.verbose,
        seconds=args.seconds,
        url=args.url,
    )
    try:
        ga.mt_process()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')
