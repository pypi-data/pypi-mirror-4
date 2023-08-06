import unittest
from ginsfsm.globals import set_global_app
from ginsfsm.gobj import (
    GObj,
    EventNotAcceptedError,
    EventError,
    StateError,
    DestinationError,
    GObjError,
    QueueError,
)

import logging
logging.basicConfig(level=logging.DEBUG)


########################################################
#       Machine samples to test filters
########################################################
#******************************
#       Transmitter
#******************************
def ac_pulse(self, event):
    self.pulses_emitted += 1
    self.broadcast_event('EV_WAVEOUT', origin=self.pulses_emitted)

FSM_TRANSMITTER = {
    'event_list': (
        'EV_PULSE',
        'EV_WAVEOUT:output',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_PULSE', ac_pulse, None),
        ),
    }
}


def event_filter(value_returned_by_action):
    if value_returned_by_action is True:
        return True
    return False


def app():
    return


def app_factory(global_config, **local_conf):
    return app

TRANSMITTER_GCONFIG = [{
    'param1': [int, 0, 0, None, ""],
    'param2': [bool, False, 0, None, ""],
    'param3': [str, 'app:xxx', 0, None, ""],
    'param4': [str, 'app:ginsfsm.tests.test_gobj2.app_factory', 0, None, ""],
}]

set_global_app('ginsfsm.tests.test_gobj2.app_factory', app)


class TransmitterGObj(GObj):
    def __init__(self):
        GObj.__init__(self, FSM_TRANSMITTER, TRANSMITTER_GCONFIG)

    def start_up(self):
        ''' Create gobj childs, initialize something...
        '''
        self.pulses_emitted = 0
        self.set_owned_event_filter(event_filter)


#******************************
#       Receptor
#******************************

def ac_wave(self, event):
    if event.origin == self.mymod:
        print("    MINE %s! pulse %s" % (self.name, event.origin))
        self.count += 1
        return True
    return False

RECEPTOR_FSM = {
    'event_list': ('EV_WAVEOUT',),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_WAVEOUT', ac_wave, None),
        ),
    }
}


RECEPTOR_GCONFIG = [{
    'transmitter': [None, None, 0, None, ""],
    'mymod': [int, 0, 0, None, ""],
}]


class ReceptorGObj(GObj):
    def __init__(self):
        GObj.__init__(self, RECEPTOR_FSM, RECEPTOR_GCONFIG)
        """ Attributes"""
        #self.transmitter = None
        #self.mymod = 0
        """ End Attributes"""
        self.count = 0

    def start_up(self):
        ''' Create gobj childs, initialize something...
        '''
        self.transmitter.subscribe_event('EV_WAVEOUT', self)


#******************************
#       Principal
#******************************

class PrincipalGObj(GObj):
    def __init__(self):
        GObj.__init__(self, {})
        self.start_up()

    def start_up(self):
        ''' Create gobj childs, initialize something...
        '''
        self.transmitter = self.create_gobj('Transmitter', TransmitterGObj, self)
        self.receptor_list = list(range(4))
        for idx in list(range(4)):
            self.receptor_list[idx] = self.create_gobj('Receptor%d' % (idx + 1),
                ReceptorGObj, self, transmitter=self.transmitter, mymod=idx + 1)

        settings = {
            'GObj.trace_mach': True,
            'GObj.logger': logging,
        }
        self.overwrite_parameters(-1, **settings)
        #for idx in range(4):
        #    self.send_event(self.transmitter, 'EV_PULSE')


########################################################
#       Tests
########################################################


class TestGObj2(unittest.TestCase):
    def setUp(self):
        self.principal = PrincipalGObj()

    def tearDown(self):
        self.principal.destroy_gobj(self.principal.transmitter)

    def test_owned_event_filter(self):
        self.principal.send_event(self.principal.transmitter, 'EV_PULSE')
        self.assertEqual(self.principal.receptor_list[0].count, 1)
        self.assertEqual(self.principal.receptor_list[1].count, 0)
        self.assertEqual(self.principal.receptor_list[2].count, 0)
        self.assertEqual(self.principal.receptor_list[3].count, 0)
        self.principal.send_event(self.principal.transmitter, 'EV_PULSE')
        self.assertEqual(self.principal.receptor_list[0].count, 1)
        self.assertEqual(self.principal.receptor_list[1].count, 1)
        self.assertEqual(self.principal.receptor_list[2].count, 0)
        self.assertEqual(self.principal.receptor_list[3].count, 0)
        self.principal.send_event(self.principal.transmitter, 'EV_PULSE')
        self.assertEqual(self.principal.receptor_list[0].count, 1)
        self.assertEqual(self.principal.receptor_list[1].count, 1)
        self.assertEqual(self.principal.receptor_list[2].count, 1)
        self.assertEqual(self.principal.receptor_list[3].count, 0)
        self.principal.send_event(self.principal.transmitter, 'EV_PULSE')
        self.assertEqual(self.principal.receptor_list[0].count, 1)
        self.assertEqual(self.principal.receptor_list[1].count, 1)
        self.assertEqual(self.principal.receptor_list[2].count, 1)
        self.assertEqual(self.principal.receptor_list[3].count, 1)

    def test_travesal_pyramid(self):
        self.assertRaises(KeyError, self.principal.__getitem__, None)
        self.assertRaises(KeyError, self.principal.__getitem__, 'XXX')
        gobj = self.principal.__getitem__('Transmitter')

    def test_overwrite_parameters(self):
        gobj = self.principal.__getitem__('Transmitter')
        settings = {
            'Transmitter.param1': 2,
            'TransmitterGObj.param2': True,
            'TransmitterGObj.param3': 'app:yyy',
        }
        gobj.overwrite_parameters(-1, **settings)
        self.assertTrue(gobj.read_parameter('param1') == 2)
        self.assertTrue(gobj.read_parameter('param2') == True)
        self.assertTrue(gobj.read_parameter('param3') == None)
        self.assertTrue(gobj.read_parameter('param4') == app)

        settings = {
            'Transmitter.param4': 'xxx',
        }
        gobj.overwrite_parameters(-1, **settings)
        self.assertTrue(gobj.read_parameter('param4') == app)
