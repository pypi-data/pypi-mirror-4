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
from ginsfsm.c_timer import GTimer
from ginsfsm.c_sock import GSock


def ac_drop(self, event):
    self.send_event(self._gsock, 'EV_DROP')


def ac_timeout_disconnected(self, event):
    if self._disabled:
        return
    if self.timeout_inactivity > 0:
        pass  # don' connect until arrives data to transmit
    else:
        self.connect()


def ac_disconnected(self, event):
    if not self._disabled:
        self.set_timeout(self.timeout_between_connections)
    if self.disconnected_event_name is not None:
        event.event_name = self.disconnected_event_name
        self.broadcast_event(event)


def ac_timeout_wait_connected(self, event):
    self.set_timeout(self.timeout_between_connections)


def ac_connected(self, event):
    self.clear_timeout()
    if self.timeout_inactivity > 0:
        self.set_timeout(self.timeout_inactivity)
    self.process_dl_tx_data()
    if self.connected_event_name is not None:
        event.event_name = self.connected_event_name
        self.broadcast_event(event)


def ac_rx_data(self, event):
    if self.timeout_inactivity > 0:
        self.set_timeout(self.timeout_inactivity)
    if self.rx_data_event_name is not None:
        event.event_name = self.rx_data_event_name
        self.broadcast_event(event)


def ac_timeout_data(self, event):
    self.send_event(self._gsock, 'EV_DROP')


def ac_tx_data(self, event):
    if self.timeout_inactivity > 0:
        self.set_timeout(self.timeout_inactivity)
    self.send_event(self._gsock, 'EV_SEND_DATA', data=event.kw['data'])


def ac_enqueue_tx_data(self, event):
    self._dl_tx_data.append(event)
    # try to connect, if this function called, is because we are disconnected.
    self.connect()


def ac_transmit_ready(self, event):
    if self.transmit_ready_event_name is not None:
        event.event_name = self.transmit_ready_event_name
        self.broadcast_event(event)

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
    'subscriber': [None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
        ],
    'disabled': [bool, False, 0, None, "Set True to disabled the connection"],
    'destinations': [list, [('', 0)], 0, None,
        "list of destination (host,port) tuples."],
    'timeout_waiting_connected': [int, 60, 0, None, ""],
    'timeout_between_connections': [int, 5, 0, None,
        "Idle timeout to wait between attempts of connection."],
    'timeout_inactivity': [int, -1, 0, None,
        "Inactivity timeout to close the connection."
        "Reconnect when new data arrived. With -1 never close."
        ],

    # If some name is None then parent don't want receive it.
    'connected_event_name': [str, 'EV_CONNECTED', 0, None,
        "Name of the *connected* event."
        " ``None`` if you want ignore the event"
        ],
    'disconnected_event_name': [str, 'EV_DISCONNECTED', 0, None,
        "Name of the *disconnected* event."
        " ``None`` if you want ignore the event"
        ],
    'transmit_ready_event_name': [str, 'EV_TRANSMIT_READY', 0, None,
        "Name of the *transmit_ready* event."
        " ``None`` if you want ignore the event"
        ],
    'rx_data_event_name': [str, 'EV_RX_DATA', 0, None,
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
        self._gsock = None
        self._idx_dst = 0
        # warning: prevent overwrite_parameters before attrs are created.
        GObj.__init__(self, CONNEX_FSM, CONNEX_GCONFIG)

    def start_up(self):
        """ Initialization zone.

        Subcribe all enabled :term:`output-event`'s to ``subscriber``
        with this sentence::

            self.subscribe_event(None, self.subscriber)
        """
        self.subscribe_event(None, self.subscriber)
        if self.name and len(self.name):
            prefix_name = self.name
        else:
            prefix_name = None

        self._gsock = self.create_gobj(
            prefix_name + '.gsock' if prefix_name else None,
            GSock,
            self,
        )
        self._gsock.get_next_dst = self.get_next_dst

        self._timer = self.create_gobj(
            prefix_name + '.timer' if prefix_name else None,
            GTimer,
            self,
            timeout_event_name='EV_TIMEOUT')
        if not self._disabled:
            self.set_timeout(2)  # self.timeout_between_connections

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        self._disabled = value
        if value:
            self.set_timeout(-1)
            self.send_event(self._gsock, 'EV_DROP')
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
        self.set_timeout(self.timeout_waiting_connected)
        self.send_event(self._gsock, 'EV_CONNECT')

    def get_next_dst(self):
        """ Return the destination (host,port) tuple to connect from
        the ``destinations`` attribute.
        If there are multiple tuples in ``destinations`` attribute,
        try to connect to each tuple cyclically.
        Override :meth:`ginsfsm.c_sock.GSock.get_next_dst`.
        """
        host, port = self.destinations[self._idx_dst]
        self._idx_dst += 1
        if self._idx_dst >= len(self.destinations):
            self._idx_dst = 0
        return (host, port)

    def process_dl_tx_data(self):
        while True:
            try:
                event = self._dl_tx_data.popleft()
            except IndexError:
                break
            else:
                self.send_event(
                    self._gsock,
                    'EV_SEND_DATA',
                    data=event.kw['data'])
