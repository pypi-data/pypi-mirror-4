import unittest

from ginsfsm.smachine import (
    SMachine,
    EMPTY_FSM,
    StateError,
    MachineError,
    EventError,
    EventNotAcceptedError,
    filter_event_attrs,
    )


class TestSuperEmptySMachine(unittest.TestCase):
    def setUp(self):
        self.fsm = SMachine({})

    def test_set_bad_smachine(self):
        self.assertRaises(MachineError, SMachine, '')

    def test_set_bad_new_state(self):
        self.assertRaises(StateError, self.fsm.set_new_state, 'STATE')
        self.assertRaises(StateError, self.fsm._set_new_state, 'STATE')
        self.assertRaises(StateError, self.fsm.set_new_state, 1)
        self.assertRaises(StateError, self.fsm._set_new_state, 1)
        self.assertRaises(StateError, self.fsm.set_new_state, {})
        self.assertRaises(StateError, self.fsm._set_new_state, {})

    def test_get_current_bad_state_name(self):
        st = self.fsm.get_current_state()
        self.assertEqual(st, None)

    def test_trace_mach(self):
        self.fsm.trace_mach = True
        self.fsm.trace_mach = False


class TestEmptySMachine(unittest.TestCase):
    def setUp(self):
        self.fsm = SMachine(EMPTY_FSM)

    def test_set_bad_new_state(self):
        self.assertRaises(StateError, self.fsm.set_new_state, 'STATE')
        self.assertRaises(StateError, self.fsm._set_new_state, 'STATE')
        self.assertRaises(StateError, self.fsm.set_new_state, 1)
        self.assertRaises(StateError, self.fsm._set_new_state, 1)
        self.assertRaises(StateError, self.fsm.set_new_state, {})
        self.assertRaises(StateError, self.fsm._set_new_state, {})

    def test_get_current_bad_state_name(self):
        st = self.fsm.get_current_state()
        self.assertEqual(st, None)


#########################################################3
#   Wrong FSM: state name is not in state_list
#########################################################3
FSM_TEST1 = {
    'event_list': (
        'EV_TIMEOUT:bottom.input',
    ),
    'state_list': (
        'ST_STATE1',
        'ST_STATEXX',
    ),
    'machine': {
        'ST_STATE1':
        (
            ('EV_TIMEOUT', None, 'ST_STATE2'),
        ),
        'ST_STATE2':
        (
            ('EV_TIMEOUT', None, 'ST_STATE1'),
        ),
    }
}


class Test1SMachineState(unittest.TestCase):
    def test(self):
        self.assertRaises(MachineError, SMachine, FSM_TEST1)

#########################################################3
#   Wrong FSM: state_list has more states than machine
#########################################################3
FSM_TEST2 = {
    'event_list': ('EV_TIMEOUT',),
    'state_list': ('ST_STATE1', 'ST_STATE2', 'ST_STATE3'),
    'machine': {
        'ST_STATE1':
        (
            ('EV_TIMEOUT',      None,       'ST_STATE2'),
        ),
        'ST_STATE2':
        (
            ('EV_TIMEOUT',      None,       'ST_STATE1'),
        ),
    }
}

class Test2SMachineState(unittest.TestCase):
    def test(self):
        self.assertRaises(MachineError, SMachine, FSM_TEST2)

#########################################################3
#   Wrong FSM: state_list has dup names
#########################################################3
FSM_TEST3 = {
    'event_list': ('EV_TIMEOUT',),
    'state_list': ('ST_STATE1', 'ST_STATE2', 'ST_STATE2'),
    'machine': {
        'ST_STATE1':
        (
            ('EV_TIMEOUT',      None,       'ST_STATE2'),
        ),
        'ST_STATE2':
        (
            ('EV_TIMEOUT',      None,       'ST_STATE1'),
        ),
    }
}


class Test3SMachineState(unittest.TestCase):
    def test(self):
        self.assertRaises(MachineError, SMachine, FSM_TEST3)

#########################################################3
#   Wrong FSM: event name is not in event_list
#########################################################3
FSM_TEST4 = {
    'event_list': ('EV_TIMEOUT1','EV_TIMEOUT2'),
    'state_list': ('ST_STATE1', 'ST_STATE2'),
    'machine': {
        'ST_STATE1':
        (
            ('EV_TIMEOUTXXX',    None,       'ST_STATE2'),
            ('EV_TIMEOUT2',      None,       'ST_STATE2'),
        ),
        'ST_STATE2':
        (
            ('EV_TIMEOUT1',      None,       'ST_STATE1'),
            ('EV_TIMEOUT2',      None,       'ST_STATE1'),
        ),
    }
}


class Test4SMachineEvent(unittest.TestCase):
    def test(self):
        self.assertRaises(MachineError, SMachine, FSM_TEST4)

#########################################################3
#   Wrong FSM: event name has more names
#########################################################3
FSM_TEST5 = {
    'event_list': ('EV_TIMEOUT1','EV_TIMEOUT2','EV_TIMEOUT3'),
    'state_list': ('ST_STATE1', 'ST_STATE2'),
    'machine': {
        'ST_STATE1':
        (
            ('EV_TIMEOUT1',      None,       'ST_STATE2'),
            ('EV_TIMEOUT2',      None,       'ST_STATE2'),
        ),
        'ST_STATE2':
        (
            ('EV_TIMEOUT1',      None,       'ST_STATE1'),
            ('EV_TIMEOUT2',      None,       'ST_STATE1'),
        ),
    }
}


class Test5SMachineEvent(unittest.TestCase):
    def test(self):
        self.assertRaises(MachineError, SMachine, FSM_TEST5)

#########################################################3
#   Wrong FSM: event name has dup names
#########################################################3
FSM_TEST6 = {
    'event_list': ('EV_TIMEOUT1','EV_TIMEOUT2','EV_TIMEOUT2'),
    'state_list': ('ST_STATE1', 'ST_STATE2'),
    'machine': {
        'ST_STATE1':
        (
            ('EV_TIMEOUT1',      None,       'ST_STATE2'),
            ('EV_TIMEOUT2',      None,       'ST_STATE2'),
        ),
        'ST_STATE2':
        (
            ('EV_TIMEOUT1',      None,       'ST_STATE1'),
            ('EV_TIMEOUT2',      None,       'ST_STATE1'),
        ),
    }
}


class Test6SMachineEvent(unittest.TestCase):
    def test(self):
        self.assertRaises(MachineError, SMachine, FSM_TEST6)

#########################################################3
#   Wrong FSM: next state name is not in state_list
#########################################################3
FSM_TEST7 = {
    'event_list': ('EV_TIMEOUT',),
    'state_list': ('ST_STATE1', 'ST_STATE2'),
    'machine': {
        'ST_STATE1':
        (
            ('EV_TIMEOUT',      None,       None),
        ),
        'ST_STATE2':
        (
            ('EV_TIMEOUT',      None,       'ST_STATE3'),
        ),
    }
}


class Test7SMachineState(unittest.TestCase):
    def test(self):
        self.assertRaises(MachineError, SMachine, FSM_TEST7)

#########################################################3
#   Wrong FSM: action is not callable
#########################################################3
FSM_TEST8 = {
    'event_list': ('EV_TIMEOUT',),
    'state_list': ('ST_STATE1', 'ST_STATE2'),
    'machine': {
        'ST_STATE1':
        (
            ('EV_TIMEOUT',      None,    None),
        ),
        'ST_STATE2':
        (
            ('EV_TIMEOUT',      'hi',       'ST_STATE2'),
        ),
    }
}


class Test8SMachineState(unittest.TestCase):
    def test(self):
        self.assertRaises(MachineError, SMachine, FSM_TEST8)


#########################################################3
#   Good FSM:
#########################################################3
def ac_test1(self, event):
    return 'OK'


def ac_test2(self, event):
    self.set_new_state('ST_STATE1')

FSM_TEST9 = {
    'event_list': (
        'EV_TEST1',
        'EV_TEST2',
        'EV_TEST3:output',
    ),
    'state_list': ('ST_STATE1', 'ST_STATE2'),
    'machine': {
        'ST_STATE1':
        (
            ('EV_TEST1',        None,           'ST_STATE2'),
        ),
        'ST_STATE2':
        (
            ('EV_TEST1',        ac_test1,       'ST_STATE2'),
            ('EV_TEST2',        ac_test2,       None),
        ),
    }
}


class Test9SMachineState(unittest.TestCase):
    def setUp(self):
        self.fsm = SMachine(FSM_TEST9)

    def test_event_list(self):
        self.assertEqual(self.fsm._event_index.get('EV_TEST1'), 1)
        self.assertEqual(self.fsm._event_index.get('EV_TEST2'), 2)
        input_event_list = self.fsm.get_event_list()
        self.assertEqual(input_event_list,
                         filter_event_attrs(FSM_TEST9['event_list']))
        output_event_list = self.fsm.get_output_event_list()
        self.assertEqual(output_event_list, ['EV_TEST3'])

    def test_state_list(self):
        self.assertEqual(self.fsm._state_index.get('ST_STATE1'), 1)
        self.assertEqual(self.fsm._state_index.get('ST_STATE2'), 2)

    def test_inject_event1(self):
        self.assertRaises(EventError, self.fsm.inject_event, 'EV_XXX')
        self.assertRaises(EventError, self.fsm.inject_event, {})
        ret = self.fsm.inject_event('EV_TEST2')
        self.assertEqual(ret, EventNotAcceptedError)
        ret = self.fsm.inject_event('EV_TEST1')
        state = self.fsm.get_current_state()
        self.assertEqual(state, 'ST_STATE2')
        self.assertEqual(ret, None)

        ret = self.fsm.inject_event('EV_TEST1')
        state = self.fsm.get_current_state()
        self.assertEqual(state, 'ST_STATE2')
        self.assertEqual(ret, 'OK')

        ret = self.fsm.inject_event('EV_TEST2')
        state = self.fsm.get_current_state()
        self.assertEqual(state, 'ST_STATE1')
        self.assertEqual(ret, None)
