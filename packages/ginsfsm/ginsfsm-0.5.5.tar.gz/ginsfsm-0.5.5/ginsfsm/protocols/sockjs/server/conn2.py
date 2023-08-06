# -*- coding: utf-8 -*-
"""
    SockJS connection interface with GOBJ
"""
from ginsfsm.gobj import GObj


def ac_on_open(self, event):
    pass


def ac_on_close(self, event):
    pass


def ac_on_message(self, event):
    """ Message received.
    """
    msg = event.msg
    self.send(msg)


SOCKJSCONNECTION_FSM = {
    'event_list': (
        'EV_ON_OPEN:bottom input',
        'EV_ON_MESSAGE:bottom input',
        'EV_ON_CLOSE:bottom input',
    ),
    'state_list': (
        'ST_IDLE',
    ),
    'machine': {
        'ST_IDLE':
        (
            ('EV_ON_OPEN',      ac_on_open,     None),
            ('EV_ON_MESSAGE',   ac_on_message,  None),
            ('EV_ON_CLOSE',     ac_on_close,    None),
        ),
    }
}

SOCKJSCONNECTION_GCONFIG = {
    'session': [None, None, 0, None, ""],
    'subscriber': [
        None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
    ],
}


class SockJSConnection(GObj):
    """  SockJSConnection GObj.

    .. ginsfsm::
       :fsm: SOCKJSCONNECTION_FSM
       :gconfig: SOCKJSCONNECTION_GCONFIG

    *Input-Events:*
        * :attr:`'EV_ON_OPEN'`: sockjs client connected.

        * :attr:`'EV_ON_MESSAGE'`: message received.

          Event attributes:
            * :attr:`msg`: the message received.

        * :attr:`'EV_ON_CLOSE'`: sockjs client disconnected.



    """
    def __init__(self):
        GObj.__init__(self, SOCKJSCONNECTION_FSM, SOCKJSCONNECTION_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """
        if self.config.subscriber is None:
            self.config.subscriber = self.parent
        self.subscribe_event(None, self.config.subscriber)

    def send(self):
        """ Transmit message to sockjs client.
        """
        self.session.send()
