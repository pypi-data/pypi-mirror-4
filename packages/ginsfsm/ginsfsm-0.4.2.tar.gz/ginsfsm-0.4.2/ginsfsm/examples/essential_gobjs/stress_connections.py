"""
GObj :class:`OnServer` and :class:`OnClient`
============================================

Utility for check a server/client :term:`gaplic`'s
running as thread or subprocesses and stress the connections.

It uses :class:`ginsfsm.c_srv_sock.GServerSock`
and :class:`ginsfsm.c_sock.GSock`.

Run two gaplics. One is the server, the other the client.

Stress with many connections.

Configuration:
    * The server can run as thread o subprocess.
    * Limit of client connections to be reached.

.. autoclass:: OnServer
    :members:

.. autoclass:: OnClient
    :members:
"""

import time
import logging
logging.basicConfig(level=logging.DEBUG)

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_timer import GTimer
from ginsfsm.c_connex import GConnex
from ginsfsm.c_srv_sock import GServerSock


#===============================================================
#                   Server
#===============================================================

def ac_clisrv_timeout(self, event):
    self.set_timeout(5)
    pass


def ac_clisrv_connected(self, event):
    if len(self.dl_childs) == 3:
        self.start_time = time.clock()

    print('connected FROM %s' % str(event.peername))
    print("Server's clients: %d" % len(self.dl_childs))

    if len(self.dl_childs) == self.connections + 2:
        end_time = time.clock()
        print("Time for %d connections: %f seconds" % (
            self.connections,
            end_time - self.start_time))


def ac_clisrv_disconnected(self, event):
    self.destroy_gobj(event.source[-1])


SERVER_FSM = {
    'event_list': (
        'EV_SET_TIMER: bottom output',
        'EV_TIMEOUT: bottom input',
        'EV_CONNECTED: bottom input',
        'EV_DISCONNECTED: bottom input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',          ac_clisrv_timeout,         None),
            ('EV_CONNECTED',        ac_clisrv_connected,       None),
            ('EV_DISCONNECTED',     ac_clisrv_disconnected,    None),
        ),
    }
}

SERVER_GCONFIG = {  # type, default_value, flag, validate_function, desc
    'verbose': [int, 0, 0, None, "Increase output verbosity. Values [0,1,2]"],
    'connections': [int, 0, 0, None, "Limit of connections to be reached."],
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

    *Output-Events:*

        * :attr:`'EV_START_TIMER'`: Start timer.

    """
    def __init__(self):
        GObj.__init__(self, SERVER_FSM, SERVER_GCONFIG)
        self.start_time = 0

    def start_up(self):
        self.timer = self.create_gobj(
            None,
            GTimer,
            self)

        self.server = self.create_gobj(
            None,
            GServerSock,
            self,
            host='127.0.0.1',
            port=8000,
            # only want receive EV_CONNECTED/EV_DISCONNECTED event
            rx_data_event_name=None,
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


#===============================================================
#                   Client
#===============================================================

def ac_client_timeout(self, event):
    if self.connex is None:
        self.connex = range(self.connections)
        for i in self.connex:
            print i
            self.connex[i] = self.create_gobj(
                'client-%02d' % i,
                GConnex,
                self,
                destinations=[('127.0.0.1', 8000)],
                # only want receive EV_CONNECTED/EV_DISCONNECTED event
                rx_data_event_name=None,
                transmit_ready_event_name=None,
            )
    self.set_timeout(10)


def ac_client_connected(self, event):
    pass


def ac_client_disconnected(self, event):
    pass


CLIENT_FSM = {
    'event_list': (
        'EV_SET_TIMER: bottom output',
        'EV_TIMEOUT: bottom input',
        'EV_CONNECTED: bottom input',
        'EV_DISCONNECTED: bottom input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',          ac_client_timeout,         None),
            ('EV_CONNECTED',        ac_client_connected,       None),
            ('EV_DISCONNECTED',     ac_client_disconnected,    None),
        ),
    }
}

CLIENT_GCONFIG = {  # type, default_value, flag, validate_function, desc
    'verbose': [int, 0, 0, None, "Increase output verbosity. Values [0,1,2]"],
    'connections': [int, 0, 0, None, "Limit of connections to be reached."],
}


class OnClient(GObj):
    """  Client GObj.

    .. ginsfsm::
       :fsm: CLIENT_FSM
       :gconfig: CLIENT_GCONFIG

    *Input-Events:*

        * :attr:`'EV_TIMEOUT'`: Timer over.
            Start the machine.

        * :attr:`'EV_CONNECTED'`: Client connected.

        * :attr:`'EV_DISCONNECTED'`: Client disconnected.

    *Output-Events:*

        * :attr:`'EV_START_TIMER'`: Start timer.

    """
    def __init__(self):
        GObj.__init__(self, CLIENT_FSM, CLIENT_GCONFIG)

    def start_up(self):
        self.timer = self.create_gobj(
            None,
            GTimer,
            self,
        )

        if self.verbose > 1:
            settings = {
                'GObj.trace_mach': True,
                'GObj.logger': logging,
            }
            self.overwrite_parameters(-1, **settings)

        self.connex = None
        self.set_timeout(1)

    def set_timeout(self, seconds):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=seconds)

    def clear_timeout(self):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=-1)


#===============================================================
#                   Main
#===============================================================
from ginsfsm.gaplic import setup_gaplic_thread, setup_gaplic_process

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "connections",
        type=int,
        nargs='?', default=400,
        help="Limit of connections to be reached."
    )
    parser.add_argument(
        "--run-as-process",
        action="store_true",
        help="Run the server as subprocess. By default it runs as thread."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        type=int,
        choices=[0, 1, 2],
        default=0,
    )
    args = parser.parse_args()
    run_as_process = args.run_as_process

    if run_as_process:
        # run server gaplic as child daemon process
        ga_srv = GAplic('Server')
        ga_srv.create_gobj(
            'server',
            OnServer,
            None,
            connections=args.connections,
            verbose=args.verbose,
        )
        srv_worker = setup_gaplic_process(ga_srv)
        srv_worker.start()

        # run client gaplic as main process
        ga_cli = GAplic('Client')
        ga_cli.create_gobj(
            'client',
            OnClient,
            None,
            connections=args.connections,
            verbose=args.verbose,
        )

        try:
            ga_cli.start()
        except (KeyboardInterrupt, SystemExit):
            ga_srv.shutdown()
            srv_worker.join()
            print('Program stopped')

    else:
        # run server gaplic as thread
        ga_srv = GAplic('Server')
        ga_srv.create_gobj(
            'server',
            OnServer,
            None,
            connections=args.connections,
            verbose=args.verbose,
        )
        srv_worker = setup_gaplic_thread(ga_srv)
        srv_worker.start()

        # run client gaplic as main process
        ga_cli = GAplic('Client')
        ga_cli.create_gobj(
            'client',
            OnClient,
            None,
            connections=args.connections,
            verbose=args.verbose,
        )

        try:
            ga_cli.start()
        except (KeyboardInterrupt, SystemExit):
            ga_srv.shutdown()
            srv_worker.join()
            print('Program stopped')
