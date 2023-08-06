import unittest

from ginsfsm.gaplic import GAplic
from ginsfsm.gobj import GObj

from ginsfsm.c_timer import GTimer

import logging
logging.basicConfig(level=logging.DEBUG)


def ac_timeout(self, event):
    self.timeout_done = True


FSM = {
    'event_list': ('EV_TIMEOUT',),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',      ac_timeout,     None),
        ),
    }
}


class GPrincipal(GObj):
    """  Principal gobj.
    """
    def __init__(self):
        GObj.__init__(self, FSM)
        self.timer = None
        self.timeout_done = False

    def start_up(self):
        """ Create child and start the timer.
        """
        self.timer = self.create_gobj(
            'timer',
            GTimer,
            self,
            timeout_event_name='EV_TIMEOUT')

        settings = {
            'GObj.trace_mach': True,
            'GObj.logger': logging,
        }
        self.overwrite_parameters(-1, **settings)

    def set_timeout(self, seconds):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=seconds)

    def clear_timeout(self):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=-1)


class TestGTimer(unittest.TestCase):
    def setUp(self):
        self.ga = GAplic(name='Test')
        self.principal = self.ga.create_gobj('principal', GPrincipal, None)

    def test_send_event(self):
        self.principal.set_timeout(2)

        while self.ga._loop():
            pass
        self.assertTrue(self.principal.timeout_done is True)


class MyGAplic(GAplic):
    dones = [0] * 3

    def mt_subprocess(self):
        i = 0
        self.principal = self.search_unique_gobj('principal')
        for done in self.dones:
            if done:
                i += 1
                continue

            if i == 0:
                self.principal.set_timeout(2)
                self.dones[i] = True

            elif i == 1:
                if self.principal.timeout_done is True:
                    self.dones[i] = True

            elif i == 2:
                exit()

            i += 1

if __name__ == "__main__":
    ga = MyGAplic('TestGAplic')
    ga.create_gobj('principal', GPrincipal, None)
    try:
        ga.mt_process()
    except KeyboardInterrupt:
        print('Program stopped')
