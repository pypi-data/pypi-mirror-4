"""
GObj :class:`OnGConnex`
=======================

Utility for check :class:`ginsfsm.c_connex.GConnex`.

Send a query to two url's alternatively.

How? send the query each 10 seconds, but set a timeout_inactivity of 5.
In each disconnection the next connection will switch between the
two destinations.

.. autoclass:: OnGConnex
    :members:

"""

import logging
logging.basicConfig(level=logging.DEBUG)

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_timer import GTimer
from ginsfsm.c_connex import GConnex
from ginsfsm.utils import hexdump

QUERY = "GET / HTTP/1.1\r\n" + \
    "Host: www\r\n" + \
    "\r\n"


def ac_rx_data(self, event):
    data = event.kw['data']
    if self.verbose:
        print('Receiving %d bytes' % len(data))
        print(hexdump('<=', data))


def ac_timeout(self, event):
    self.send_event(self.connex, 'EV_SEND_DATA', data=QUERY)
    self.set_timeout(10)


ONGCONNEX_FSM = {
    'event_list': (
        'EV_SET_TIMER: bottom output',
        'EV_TIMEOUT:bottom input',
        'EV_RX_DATA:bottom input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',      ac_timeout,     'ST_IDLE'),
            ('EV_RX_DATA',      ac_rx_data,     'ST_IDLE'),
        ),
    }
}


ONGCONNEX_GCONFIG = {  # type, default_value, flag, validate_function, desc
    'verbose': [int, 0, 0, None, "Increase output verbosity. Values [0,1,2]"],
    'url1': [str, 'www.google.com', 0, None, "Url one to connect."],
    'url2': [str, 'www.twitter.com', 0, None, "Url two to connect."],
}


class OnGConnex(GObj):
    """  OnGConnex GObj.

    .. ginsfsm::
       :fsm: ONGCONNEX_FSM
       :gconfig: ONGCONNEX_GCONFIG

    *Input-Events:*

        * :attr:`'EV_TIMEOUT'`: Timer over.
            Start the machine.

        * :attr:`'EV_RX_DATA'`: Receiving data.
            Receiving data from urls.

    *Output-Events:*

        * :attr:`'EV_START_TIMER'`: Start timer.

    """
    def __init__(self):
        GObj.__init__(self, ONGCONNEX_FSM, ONGCONNEX_GCONFIG)

    def start_up(self):
        """ Initialization zone."""
        self.timer = self.create_gobj(
            None,
            GTimer,
            self,
        )

        self.connex = self.create_gobj(
            'connex',
            GConnex,
            self,
            destinations=[
                (self.url1, 80),
                (self.url2, 80),
            ],
            timeout_inactivity=5,
            # only want receive EV_RX_DATA event
            connected_event_name=None,
            disconnected_event_name=None,
            transmit_ready_event_name=None,
        )

        if self.verbose > 1:
            settings = {
                'GObj.trace_mach': True,
                'GObj.logger': logging,
            }
            self.overwrite_parameters(-1, **settings)

        self.set_timeout(5)

    def set_timeout(self, seconds):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=seconds)

    def clear_timeout(self):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=-1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url1",
        nargs='?', default='www.google.es',
        help="First url to connect."
    )
    parser.add_argument(
        "url2",
        nargs='?', default='www.twitter.es',
        help="Second url to connect."
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
        'ongconnex',
        OnGConnex,
        None,
        verbose=args.verbose,
        url1=args.url1,
        url2=args.url2,
    )
    try:
        ga.mt_process()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')
