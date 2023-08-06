"""
GObj :class:`OnServer`
======================

Stress with many connections and many data.

To run with :mod:`ginsfsm.examples.stress_client_echo`

The server echo the data.

It uses :class:`ginsfsm.c_srv_sock.GServerSock`.

.. autoclass:: OnServer
    :members:

"""

import logging
logging.basicConfig(level=logging.DEBUG)

from ginsfsm.smachine import SMachine
from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_timer import GTimer
from ginsfsm.c_srv_sock import GServerSock

#===============================================================
#                   Server
#===============================================================
n_connected_clisrv = 0


def ac_clisrv_timeout(self, event):
    self.set_timeout(10)
    print "Server's clients: %d, connected %d" % (
        len(self.dl_childs), n_connected_clisrv)


def ac_clisrv_connected(self, event):
    global n_connected_clisrv
    n_connected_clisrv += 1


def ac_clisrv_disconnected(self, event):
    global n_connected_clisrv
    n_connected_clisrv -= 1
    self.destroy_gobj(event.source[-1])


def ac_clisrv_rx_data(self, event):
    #print 'recibo:', event.data
    # Do echo
    self.send_event(event.source[-1], 'EV_SEND_DATA', data=event.data)


SERVER_FSM = {
    'event_list': (
        'EV_SET_TIMER: bottom output',
        'EV_TIMEOUT: bottom input',
        'EV_CONNECTED: bottom input',
        'EV_DISCONNECTED: bottom input',
        'EV_RX_DATA:bottom input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',          ac_clisrv_timeout,         'ST_IDLE'),
            ('EV_CONNECTED',        ac_clisrv_connected,       'ST_IDLE'),
            ('EV_DISCONNECTED',     ac_clisrv_disconnected,    'ST_IDLE'),
            ('EV_RX_DATA',          ac_clisrv_rx_data,         'ST_IDLE'),
        ),
    }
}


SERVER_GCONFIG = {  # type, default_value, flag, validate_function, desc
    'verbose': [int, 1, 0, None, "Increase output verbosity. Values [0,1,2]"],
}


class OnServer(GObj):
    """  Server GObj.

    .. ginsfsm::
       :fsm: SERVER_FSM
       :gconfig: SERVER_GCONFIG

    *Input-Events:*

        * :attr:`'EV_TIMEOUT'`: Timer over.
            Start the machine.

        * :attr:`'EV_CONNECTED'`: New client.

        * :attr:`'EV_DISCONNECTED'`: Client disconnected.

        * :attr:`'EV_RX_DATA'`: Receiving data.

    *Output-Events:*

        * :attr:`'EV_START_TIMER'`: Start timer.

    """
    def __init__(self):
        GObj.__init__(self, SERVER_FSM, SERVER_GCONFIG)

    def start_up(self):
        self.timer = self.create_gobj(
            None,
            GTimer,
            self)
        self.set_timeout(5)

        self.server = self.create_gobj(
            None,
            GServerSock,
            self,
            host='0.0.0.0',
            port=8000,
            transmit_ready_event_name=None,
        )

        if self.verbose > 0:
            settings = {
                'GObj.trace_mach': True,
                'GObj.logger': logging,
            }
            self.overwrite_parameters(-1, **settings)
            SMachine.__global_trace_mach = True

    def set_timeout(self, seconds):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=seconds)

    def clear_timeout(self):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=-1)


#===============================================================
#                   Main
#===============================================================
if __name__ == "__main__":
    ga_srv = GAplic('Server')
    ga_srv.create_gobj(
        'server',
        OnServer,
        None,
    )

    try:
        ga_srv.mt_process()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')
