"""
GObj :class:`OnClient`
======================

Stress with many connections and many data.

To run against :mod:`ginsfsm.examples.stress_server_echo`

The server echo the data.

It uses :class:`ginsfsm.c_connex.GConnex`.

.. autoclass:: OnClient
    :members:

"""

import datetime

import logging
logging.basicConfig(level=logging.DEBUG)

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_timer import GTimer
from ginsfsm.c_connex import GConnex

#===============================================================
#                   Client
#===============================================================
query = "GET / HTTP/1.1\r\n" + \
    "Host: \r\n" + \
    "\r\n"


def ac_client_timeout(self, event):
    if self.connex is None:
        self.connex = range(self.connections)

    if self.n_clients < self.connections:
        for i in range(self.n_clients, self.connections):
            self.n_clients += 1
            self.connex[i] = self.create_gobj(
                'client-%d' % i,
                GConnex,  # GSock,
                self,
                destinations=[(self.host, self.port)],
                transmit_ready_event_name=None,
            )

            self.connex[i].idx = i
            self.connex[i].conectado = 0
            self.connex[i].sended_msgs = 0
            self.connex[i].received_msgs = 0
            #self.connex[i].mt_connect(host='172.21.228.211', port=8084)
            #ret = self.connex[i].mt_connect(host='127.0.0.1', port=8000) #8082
            #if not ret:
            #    break
    print "conectados: %d" % self.n_connected_clients
    if self.n_connected_clients == self.connections:
        n_echoes = 0
        n_total = 0
        diff = datetime.timedelta(seconds=0)
        for cli in self.connex:
            #print 'cli %d txed_msgs %d, rxed_msgs %d' % (cli.idx, cli._gsock.txed_msgs, cli._gsock.rxed_msgs)
            if cli._gsock.rxed_msgs == cli._gsock.txed_msgs:
                n_total += 1
            if cli.sended_msgs == cli.received_msgs:
                n_echoes += 1
            diff += self.diff
        print "Echoes OK: %d of %d, taverage %s" % (n_echoes, self.connections, diff/self.connections)

        for cli in self.connex:
            if cli._gsock.connected:
                cli.sended_msgs = 1
                cli.received_msgs = 0
                cli.tx_time = datetime.datetime.now()
                self.send_event(cli, 'EV_SEND_DATA', data=query) #data="HOLA")

    self.set_timeout(10)


def ac_client_connected(self, event):
    if not event.source[-1].conectado:
        self.n_connected_clients += 1
        event.source[-1].conectado = 1
    print "C: conectados: %d" % self.n_connected_clients


def ac_client_disconnected(self, event):
    if event.source[-1].conectado:
        self.n_connected_clients -= 1
        event.source[-1].conectado = 0
    print "D: conectados: %d" % self.n_connected_clients


def ac_client_rx_data(self, event):
    cli = self.connex[event.source[-1].idx]
    cli.received_msgs += 1
    cli.rx_time = datetime.datetime.now()
    diff = cli.rx_time - cli.tx_time
    if diff < self.min_response_time:
        self.min_response_time = diff
    if diff > self.max_response_time:
        self.max_response_time = diff
    self.diff = diff
    #print 'recibo:', event.data
    #print 'diff %s, min %s, max %s' % (diff, self.min_response_time, self.max_response_time)


CLIENT_FSM = {
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
            ('EV_TIMEOUT',          ac_client_timeout,         'ST_IDLE'),
            ('EV_CONNECTED',        ac_client_connected,       'ST_IDLE'),
            ('EV_DISCONNECTED',     ac_client_disconnected,    'ST_IDLE'),
            ('EV_RX_DATA',          ac_client_rx_data,         'ST_IDLE'),
        ),
    }
}


CLIENT_GCONFIG = {  # type, default_value, flag, validate_function, desc
    'verbose': [int, 0, 0, None, "Increase output verbosity. Values [0,1,2]"],
    'connections': [int, 0, 0, None, "Limit of connections to be reached."],
    'host': [str, '127.0.0.1', 0, None, "Port."],
    'port': [int, 8000, 0, None, "Port."],
}


class OnClient(GObj):
    """  Client GObj.

    .. ginsfsm::
       :fsm: CLIENT_FSM
       :gconfig: CLIENT_GCONFIG

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
        GObj.__init__(self, CLIENT_FSM, CLIENT_GCONFIG)
        self.n_clients = 0
        self.n_connected_clients = 0

    def start_up(self):
        self.timer = self.create_gobj(
            None,
            GTimer,
            self
        )
        self.connex = None
        self.sended_msgs = 0
        self.received_msgs = 0
        self.min_response_time = datetime.timedelta(seconds=100)
        self.max_response_time = datetime.timedelta(seconds=0)
        self.diff = datetime.timedelta(seconds=0)

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


#===============================================================
#                   Main
#===============================================================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "host",
        nargs='?', default='127.0.0.1',
        help="Host."
    )
    parser.add_argument(
        "port",
        type=int,
        nargs='?', default=8000,
        help="Port."
    )
    parser.add_argument(
        "connections",
        type=int,
        nargs='?', default=100,
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

    ga_cli = GAplic('Client')
    ga_cli.create_gobj(
        'client',
        OnClient,
        None,
        host=args.host,
        port=args.port,
        connections=args.connections,
    )

    try:
        ga_cli.mt_process()
    except (KeyboardInterrupt, SystemExit):
        from ginsfsm.c_sock import close_all_sockets
        close_all_sockets(ga_cli._socket_map)
        print('Program stopped')
