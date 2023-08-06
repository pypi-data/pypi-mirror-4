"""
GObj :class:`OnTimer`
=====================

Utility for executing a ``command`` cyclically each ``seconds`` seconds.

The timer is supplied by :class:`ginsfsm.c_timer.GTimer`.

Dependencies:

* Envoy: `Subprocesses for Humans by kennethreitz \
<https://github.com/kennethreitz/envoy>`_.

.. autoclass:: OnTimer
    :members:

"""
import envoy

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_timer import GTimer

import logging
logging.basicConfig(level=logging.DEBUG)


def ac_exec_command(self, event):
    if self.verbose:
        print('Executing %s...' % self.command)

    response = envoy.run(self.command)

    if self.verbose:
        print(response.std_out)

    self.send_event(self.timer, 'EV_SET_TIMER', seconds=self.seconds)


ONTIMER_FSM = {
    'event_list': (
        'EV_SET_TIMER: bottom output',
        'EV_TIMEOUT: bottom input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT', ac_exec_command, 'ST_IDLE'),
        ),
    }
}

ONTIMER_GCONFIG = {  # type, default_value, flag, validate_function, desc
    'seconds': [int, 2, 0, None, "Seconds to repeat the command."],
    'verbose': [int, 0, 0, None, "Increase output verbosity. Values [0,1,2]"],
    'command': [str, 'ls', 0, None, "Command to execute."],
}


class OnTimer(GObj):
    """  OnTimer GObj.

    .. ginsfsm::
       :fsm: ONTIMER_FSM
       :gconfig: ONTIMER_GCONFIG

    *Input-Events:*

        * :attr:`'EV_TIMEOUT'`: Timer over.
            Execute the ``command``.

    *Output-Events:*

        * :attr:`'EV_START_TIMER'`: Start timer.

    """
    def __init__(self):
        GObj.__init__(self, ONTIMER_FSM, ONTIMER_GCONFIG)

    def start_up(self):
        """
        """
        self.timer = self.create_gobj(
            None,       # unnamed gobj
            GTimer,     # gclass
            self        # parent
        )

        if self.verbose > 1:
            settings = {
                'GObj.trace_mach': True,
                'GObj.logger': logging,
            }
            self.overwrite_parameters(-1, **settings)

        self.send_event(self.timer, 'EV_SET_TIMER', seconds=self.seconds)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "seconds",
        type=int,
        nargs='?', default=2,
        help="Seconds to repeat the command."
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        default='ls',
        help="Command to execute."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        type=int,
        choices=[0, 1, 2],
        default=2,
    )
    args = parser.parse_args()

    ga = GAplic()
    ga.create_gobj(
        'ontimer',
        OnTimer,
        None,
        verbose=args.verbose,
        seconds=args.seconds,
        command=''.join(args.command) or 'ls')
    try:
        ga.mt_process()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')
