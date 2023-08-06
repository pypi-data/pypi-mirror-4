from collections import deque
import unittest

from ginsfsm.gaplic import GAplic
from ginsfsm.gobj import GObj, NotUniqueGObjError
from ginsfsm.c_timer import GTimer

import logging
logging.basicConfig(level=logging.DEBUG)


def ac_check_queue(self, event):
    tx_events = 0
    while len(self.dl_query):
        try:
            data = self.dl_query.popleft()
        except IndexError:
            break
        else:
            self.send_event(self, 'EV_QUERY', data=data)
            tx_events += 1
    return tx_events


def ac_send_query(self, event):
    data = event.data
    self.send_event(self.timer, 'EV_SET_TIMER', seconds=0)  # simulate timeout
    return data


def ac_timeout_wait_resp(self, event):
    self.set_new_state('ST_IDLE')
    self.send_event(self.timer, 'EV_SET_TIMER', seconds=0)  # simulate timeout


def ac_enqueue_query(self, event):
    data = event.data
    self.dl_query.append(data)


FSM = {
    'event_list': (
        'EV_QUERY:output',
        'EV_TIMEOUT',
    ),
    'state_list': ('ST_IDLE', 'ST_WAIT_RESP'),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',    ac_check_queue,           None),
            ('EV_QUERY',      ac_send_query,            'ST_WAIT_RESP'),
        ),

        'ST_WAIT_RESP':
        (
            ('EV_TIMEOUT',    ac_timeout_wait_resp,     None),
            ('EV_QUERY',      ac_enqueue_query,         None),
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
        self.dl_query = deque()


class TestGAplic(unittest.TestCase):
    def setUp(self):
        self.gaplic = GAplic(name='TestGAplic')
        self.principal = self.gaplic.create_gobj('principal', GPrincipal, None)

    def tearDown(self):
        self.gaplic.destroy_gobj(self.principal)

    def test_create_gobj(self):
        self.assertRaises(NotUniqueGObjError,
            self.gaplic.create_gobj, 'principal', GPrincipal, None)

    def test_named_subscribe(self):
        self.principal.subscribe_event('EV_QUERY', 'principal')

    def test_send_event(self):
        data = 'XXX'
        state = self.principal.get_current_state()
        self.assertEqual(state, 'ST_IDLE')
        ret = self.principal.send_event('principal', 'EV_QUERY', data=data)
        self.assertEqual(ret, data)
        state = self.principal.get_current_state()
        self.assertEqual(state, 'ST_WAIT_RESP')
        ret = self.principal.send_event(self.principal, 'EV_QUERY', data=data)
        self.assertEqual(ret, None)
        self.assertEqual(len(self.principal.dl_query), 1)
        #self.gaplic.mt_process()
        self.gaplic._loop()
        self.gaplic._loop()
        state = self.principal.get_current_state()
        self.assertEqual(state, 'ST_IDLE')
        self.assertEqual(len(self.principal.dl_query), 1)
        #self.gaplic.mt_process()
        self.gaplic._loop()
        self.gaplic._loop()
        self.assertEqual(len(self.principal.dl_query), 0)
