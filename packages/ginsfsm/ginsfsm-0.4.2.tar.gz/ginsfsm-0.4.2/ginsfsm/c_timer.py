# -*- encoding: utf-8 -*-
"""
GObj :class:`GTimer`
====================

GObj for generate timeout events.

.. autoclass:: GTimer
    :members:
"""

from ginsfsm.gobj import GObj


def ac_set_timer(self, event):
    self.overwrite_few_parameters(['seconds', 'autostart'], **event.kw)
    if self._timer_id:
        # Clear the current timer
        self.gaplic._clearTimeout(self._timer_id)
        self._timer_id = None

    if self.seconds != -1:
        self._timer_id = self.gaplic._setTimeout(
            self.seconds,
            self._got_timer,
            autostart=self.autostart)


TIMER_FSM = {
    'event_list': (
        'EV_SET_TIMER: top,input',
        'EV_TIMEOUT: top,output',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_SET_TIMER', ac_set_timer, None),
        ),
    }
}

TIMER_GCONFIG = {
    'subscriber': [None, None, 0, None,
        "subcriber of all output-events."
        " Default is ``None``, i.e., the parent"
        ],
    'timeout_event_name': [str, 'EV_TIMEOUT', 0, None,
        "Timeout event name"],
    'seconds': [int, -1, 0, None,
        "timeout in seconds."
        " With ``seconds=-1`` the current timer is cancelled"],
    'autostart': [bool, False, 0, None,
        "If ``True`` then timeout event is repeated every ``seconds``"],
}


class GTimer(GObj):
    """  Supply timer events.

    Broadcast the ``timeout_event_name`` event
    when the ``seconds`` time has elapsed.

    If ``autostart`` is ``True``, the timer is cyclic.

    .. ginsfsm::
       :fsm: TIMER_FSM
       :gconfig: TIMER_GCONFIG

    *Input-Events:*

        * :attr:`'EV_SET_TIMER'`: Set the timer.
            Broadcast the ``'EV_TIMEOUT'`` or ``timeout_event_name`` event
            when the ``seconds`` time has elapsed.

            If ``autostart`` is true, the timer is cyclic.

            Associated data to event:

            * ``seconds``: seconds of timer.
            * ``autostart``: cyclic timer.

            With ``seconds=-1`` the current timer is cancelled.

    *Output-Events:*

        * :attr:`'EV_TIMEOUT'`: Timer over.
            Send the ``'EV_TIMEOUT'`` or ``timeout_event_name`` event
            to subscribers.

    """

    def __init__(self):
        GObj.__init__(self, TIMER_FSM, TIMER_GCONFIG)
        self._timer_id = None

    def start_up(self):
        """
        Subcribe the *output-events* to ``subscriber``.

        The output-events are broadcasting using ``post_event()``,
        forcing to get timeout events by queue, not directly.
        """
        if self.subscriber is None:
            self.subscriber = self.parent
        # force use post_event(), to get timeout events by queue, not directly
        self.subscribe_event(None, self.subscriber, use_post_event=True)

    def _got_timer(self):
        """ Callback timer
        """
        self.broadcast_event(self.timeout_event_name)
