# -*- encoding: utf-8 -*-
"""
GObj :class:`GConnex`
=====================

GObj for manage socket connection handshake.

.. autoclass:: GConnex
    :members: start_up, get_next_dst

"""
from collections import deque

from ginsfsm.gobj import GObj
from ginsfsm.gconfig import GConfig
from ginsfsm.c_timer import GTimer
from ginsfsm.c_sock import GSock


def ac_drop(self, event):
    self.send_event(self.gsock, 'EV_DROP')


def ac_timeout_disconnected(self, event):
    if self._disabled:
        return
    if self.config.timeout_inactivity > 0:
        pass  # don' connect until arrives data to transmit
    else:
        self.connect()


def ac_disconnected(self, event):
    if not self.disabled:
        if self.cycle > 0:
            self.cycle -= 1
            self.set_timeout(0.01)
        else:
            self.cycle = len(self.config.destinations)
            if self.cycle < 2:
                self.cycle = 0
            self.set_timeout(self.config.timeout_between_connections)

    if self.config.disconnected_event_name is not None:
        if self.inform_disconnected:
            event.event_name = self.config.disconnected_event_name
            self.broadcast_event(event, connex=self)
            self.inform_disconnected = False


def ac_timeout_wait_connected(self, event):
    self.set_timeout(self.config.timeout_between_connections)


def ac_connected(self, event):
    self.clear_timeout()
    self.inform_disconnected = True
    if self.config.timeout_inactivity > 0:
        self.set_timeout(self.config.timeout_inactivity)
    self.process_dl_tx_data()
    if self.config.connected_event_name is not None:
        event.event_name = self.config.connected_event_name
        self.broadcast_event(event, connex=self)


def ac_rx_data(self, event):
    if self.config.timeout_inactivity > 0:
        self.set_timeout(self.config.timeout_inactivity)
    if self.config.rx_data_event_name is not None:
        event.event_name = self.config.rx_data_event_name
        self.broadcast_event(event, connex=self)


def ac_timeout_data(self, event):
    self.send_event(self.gsock, 'EV_DROP')


def ac_tx_data(self, event):
    if self.config.timeout_inactivity > 0:
        self.set_timeout(self.config.timeout_inactivity)
    self.send_event(self.gsock, 'EV_SEND_DATA', data=event.kw['data'])


def ac_enqueue_tx_data(self, event):
    self._dl_tx_data.append(event)
    # try to connect, if this function called, is because we are disconnected.
    self.connect()


def ac_transmit_ready(self, event):
    if self.config.transmit_ready_event_name is not None:
        event.event_name = self.config.transmit_ready_event_name
        self.broadcast_event(event, connex=self)

CONNEX_FSM = {
    'event_list': (
        'EV_DROP:top input:bottom output',
        'EV_SEND_DATA:top input:bottom output ST_CONNECTED',
        'EV_CONNECTED:bottom input:top output',
        'EV_DISCONNECTED:bottom input:top output',
        'EV_RX_DATA:bottom input:top output',
        'EV_TRANSMIT_READY:bottom input:top output',
        'EV_SET_TIMER:bottom output',
        'EV_TIMEOUT:bottom input',
    ),
    'state_list': (
        'ST_DISCONNECTED',
        'ST_WAIT_CONNECTED',
        'ST_CONNECTED'
    ),
    'machine': {
        'ST_DISCONNECTED':
        (
            ('EV_SEND_DATA',      ac_enqueue_tx_data,        None),
            ('EV_TIMEOUT',        ac_timeout_disconnected,   None),
        ),
        'ST_WAIT_CONNECTED':
        (
            ('EV_SEND_DATA',      ac_enqueue_tx_data,        None),
            ('EV_CONNECTED',      ac_connected,              'ST_CONNECTED'),
            ('EV_DISCONNECTED',   ac_disconnected,           'ST_DISCONNECTED'),
            ('EV_TIMEOUT',        ac_timeout_wait_connected, 'ST_DISCONNECTED'),
        ),
        'ST_CONNECTED':
        (
            ('EV_SEND_DATA',      ac_tx_data,                None),
            ('EV_DROP',           ac_drop,                   None),
            ('EV_DISCONNECTED',   ac_disconnected,           'ST_DISCONNECTED'),
            ('EV_TIMEOUT',        ac_timeout_data,           None),
            ('EV_RX_DATA',        ac_rx_data,                None),
            ('EV_TRANSMIT_READY', ac_transmit_ready,         None),
        ),
    }
}

CONNEX_GCONFIG = {
    'subscriber': [
        None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
    ],
    'disabled': [
        bool, False, GConfig.FLAG_DIRECT_ATTR, None,
        "Set True to disabled the connection"
    ],
    'destinations': [
        list, [('', 0)], 0, None,
        "list of destination (host,port) tuples."
    ],
    'timeout_waiting_connected': [int, 60, 0, None, ""],
    'timeout_between_connections': [
        int, 5, 0, None,
        "Idle timeout to wait between attempts of connection."
    ],
    'timeout_inactivity': [
        int, -1, 0, None,
        "Inactivity timeout to close the connection."
        "Reconnect when new data arrived. With -1 never close."
    ],
    'host': [
        str, '', GConfig.FLAG_DIRECT_ATTR, None,
        "server or client host (ip or name)"
    ],
    'port': [
        int, 0, GConfig.FLAG_DIRECT_ATTR, None,
        "server or client port"
    ],

    # If some name is None then parent don't want receive it.
    'connected_event_name': [
        str, 'EV_CONNECTED', 0, None,
        "Name of the *connected* event."
        " ``None`` if you want ignore the event"
    ],
    'disconnected_event_name': [
        str, 'EV_DISCONNECTED', 0, None,
        "Name of the *disconnected* event."
        " ``None`` if you want ignore the event"
    ],
    'transmit_ready_event_name': [
        str, 'EV_TRANSMIT_READY', 0, None,
        "Name of the *transmit_ready* event."
        " ``None`` if you want ignore the event"
    ],
    'rx_data_event_name': [
        str, 'EV_RX_DATA', 0, None,
        "Name of the *rx_data* event."
        " ``None`` if you want ignore the event"
    ],
}


class GConnex(GObj):
    """  GConnex gobj.
    Responsible for maintaining the client socket connected, or not.
    It can maintain the connection closed, until new data arrived.
    It can have several destinations to connect.

    .. ginsfsm::
       :fsm: CONNEX_FSM
       :gconfig: CONNEX_GCONFIG

    *Input-Events:*
        * :attr:`'EV_SEND_DATA'`: transmit ``event.data``.

          Mandatory attributes of the received :term:`event`:

          * ``data``: data to send.

    *Output-Events:*
        * :attr:`'EV_CONNECTED'`: socket connected.

          Attributes added to the sent :term:`event`:

            * ``peername``: remote address to which the socket is connected.
            * ``sockname``: the socket’s own address.

        * :attr:`'EV_DISCONNECTED'`: socket disconnected.
        * :attr:`'EV_TRANSMIT_READY'`: socket ready to transmit more data.
        * :attr:`'EV_RX_DATA'`: data received.
          Attributes added to the sent :term:`event`:

            * ``data``: Data received from remote address.

    """
    def __init__(self):
        self._dl_tx_data = deque()  # queue for tx data.
        self._timer = None
        self._disabled = False
        #TODO: give access to _gsock properties: rx/tx msgs, etc
        self.gsock = None
        self._idx_dst = 0
        # warning: prevent overwrite_parameters before attrs are created.
        GObj.__init__(self, CONNEX_FSM, CONNEX_GCONFIG)
        self.cycle = 0
        self.inform_disconnected = False  # inform only after connected

    def start_up(self):
        """ Initialization zone.

        Subcribe all enabled :term:`output-event`'s to ``subscriber``
        with this sentence::

            self.subscribe_event(None, self.subscriber)
        """
        if self.config.subscriber is None:
            self.config.subscriber = self.parent
        self.subscribe_event(None, self.config.subscriber)

        self.cycle = len(self.config.destinations)
        if self.cycle < 2:
            self.cycle = 0

        self.gsock = self.create_gobj(
            'gsock' if self.name else None,
            GSock,
            self,
        )
        self.gsock.get_next_dst = self.get_next_dst

        self._timer = self.create_gobj(
            'timer' if self.name else None,
            GTimer,
            self,
            timeout_event_name='EV_TIMEOUT')
        if not self._disabled:
            self.set_timeout(2)  # self.config.timeout_between_connections

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        self._disabled = value
        if value:
            self.set_timeout(-1)
            self.send_event(self.gsock, 'EV_DROP')
        else:
            self.set_timeout(2)

    def set_timeout(self, seconds):
        if self._timer:  # protect from overwrite_parameters
            self.send_event(self._timer, 'EV_SET_TIMER', seconds=seconds)

    def clear_timeout(self):
        if self._timer:  # protect from overwrite_parameters
            self.send_event(self._timer, 'EV_SET_TIMER', seconds=-1)

    def connect(self):
        self.set_new_state('ST_WAIT_CONNECTED')
        self.set_timeout(self.config.timeout_waiting_connected)
        self.send_event(self.gsock, 'EV_CONNECT')

    def is_closed(self):
        # TODO: avoid direct access to gsock
        return not self.gsock.socket

    def is_disconnected(self):
        # TODO: avoid direct access to gsock
        return not self.gsock.connected

    def get_next_dst(self):
        """ Return the destination (host,port) tuple to connect from
        the ``destinations`` attribute.
        If there are multiple tuples in ``destinations`` attribute,
        try to connect to each tuple cyclically.
        Override :meth:`ginsfsm.c_sock.GSock.get_next_dst`.
        """
        host, port = self.config.destinations[self._idx_dst]
        self._idx_dst += 1
        if self._idx_dst >= len(self.config.destinations):
            self._idx_dst = 0
        return (host, port)

    @property
    def host(self):
        return self.gsock.config.host

    @host.setter
    def host(self, xx):
        pass

    @property
    def port(self):
        return self.gsock.config.port

    @port.setter
    def port(self, xx):
        pass

    def process_dl_tx_data(self):
        while True:
            try:
                event = self._dl_tx_data.popleft()
            except IndexError:
                break
            else:
                self.send_event(
                    self.gsock,
                    'EV_SEND_DATA',
                    data=event.kw['data'])
