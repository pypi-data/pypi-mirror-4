import unittest

from ginsfsm.gaplic import (
    GAplic,
    setup_gaplic_process,
    setup_gaplic_thread,
    )
from ginsfsm.gobj import GObj
from ginsfsm.c_timer import GTimer
from ginsfsm.globals import (
    get_global_main_gaplic,
    set_global_main_gaplic,
    get_global_threads,
    get_global_subprocesses,
    shutdown,
    )

import logging
logging.basicConfig(level=logging.DEBUG)


def ac_timeout(self, event):
    self.counter += 1
    if self.counter < 10:
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=1)


FSM = {
    'event_list': ('EV_TIMEOUT',),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',    ac_timeout,           None),
        ),
    }
}


class GPrincipal(GObj):
    """  Principal gobj.
    """
    def __init__(self):
        GObj.__init__(self, FSM)

    def start_up(self):
        """ Create child and start the timer.
        """
        self.timer = self.create_gobj(
            None,       # unnamed gobj
            GTimer,     # gclass
            self        # parent
        )
        settings = {
            'GObj.trace_mach': True,
            'GObj.logger': logging,
        }
        self.overwrite_parameters(-1, **settings)
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=1)
        self.counter = 0


class MyGAplic(GAplic):
    counter = 0

    def mt_subprocess(self):
        self.counter += 1
        if self.counter > 10:
            shutdown()


def setup():
    ga = GAplic('GAplic-Subprocess')
    ga.create_gobj('principal-subprocess', GPrincipal, None)
    worker = setup_gaplic_process(ga)
    worker.start()

    ga = GAplic('GAplic-Thread')
    ga.create_gobj('principal-thread', GPrincipal, None)
    worker = setup_gaplic_thread(ga)
    worker.start()

    ga = MyGAplic('GAplic-Main')
    ga.create_gobj('principal-main', GPrincipal, None)
    set_global_main_gaplic(ga)
    #ga.start()
    return ga


class TestGAplic(unittest.TestCase):
    def setUp(self):
        self.ga = setup()

    def test_named_subscribe(self):
        while self.ga._loop():
            pass
        shutdown()

if __name__ == "__main__":
    setup()
