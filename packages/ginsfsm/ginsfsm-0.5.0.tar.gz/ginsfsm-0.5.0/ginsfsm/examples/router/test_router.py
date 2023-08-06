# -*- encoding: utf-8 -*-
"""
Routing events between gaplics.
===============================

You can run this file with ``gserve test_router.ini``

.. autoclass:: Sample1
    :members:

.. autoclass:: Sample2
    :members:


In this example:
    TITI gaplic of main thread
    TOTO gaplic another thread or subprocess

TOTO enable router server in port 8000
TITI add static router to localhost:8000

TOTO has EV_SET_TIMEOUT Api.
    Its action is set a timeout that broadcast EV_MESSAGE.

TITI do two things:
    - subscribe to event EV_MESSAGE of external TOTO
    - send EV_SET_TIMEOUT to external TOTO

    The EV_SET_TIMEOUT event reachs TOTO,
    then it set the timer that broadcast EV_MESSAGE.

    TITI receive the external EV_MESSAGE because it's subscribe it.

    When TITI receive the EV_MESSAGE,
    re-send EV_SET_TIMEOUT to external TOTO
    and so on.

"""
import logging
logging.basicConfig(level=logging.DEBUG)

from ginsfsm.gaplic import GAplic
from ginsfsm.c_timer import GTimer
from ginsfsm.gobj import GObj
from ginsfsm.globals import (
    list_globals,
)


#===============================================================
#                   GAplic TITI
#===============================================================
def ac_message(self, event):
    print("ORDENNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN %s %s" % (
        self.counter,
        event.__subscription_reference__,
    ))
    list_globals()
    self.counter += 1
    if self.counter > 4:
        # delete subscription
        ret = self.gaplic.unsubscribe_event_from_external_gaplic(
            'TOTO',         # gaplic_name
            'sample2',      # gobj_name
            'EV_MESSAGE',   # event_name
            self,           # subscriber_gobj
            __subscription_reference__=event.__subscription_reference__,
        )
        if not ret:
            print("Eiiiiiiiiiiiiiiiiiiiiii something wrong!")

    # causes broadcast EV_MESSAGE again
    self.gaplic.send_event_to_external_gaplic(
        'TOTO',             # gaplic_name
        'sample2',          # gobj_name
        'EV_SET_TIMEOUT',   # event_name
        self,               # subscriber_gobj
        timeout=2,
    )


SAMPLE1_FSM = {
    'event_list': (
        'EV_MESSAGE: top input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_MESSAGE', ac_message, None),
        ),
    }
}

SAMPLE1_GCONFIG = {  # type, default_value, flag, validate_function, desc
}


class Sample1(GObj):
    """  Sample1 GObj.

    .. ginsfsm::
       :fsm: SAMPLE1_FSM
       :gconfig: SAMPLE1_GCONFIG

    *Input-Events:*

        * :attr:`'EV_MESSAGE'`: .

    *Output-Events:*

    """
    def __init__(self):
        GObj.__init__(self, SAMPLE1_FSM, SAMPLE1_GCONFIG)
        self.counter = 0

    def start_up(self):
        """
        """
        ret = self.gaplic.subscribe_event_from_external_gaplic(
            'TOTO',         # gaplic_name
            'sample2',      # gobj_name
            'EV_MESSAGE',   # event_name
            self,           # subscriber_gobj
        )
        if not ret:
            print("Eiiiiiiiiiiiiiiiiiiiiii something wrong!")

        self.gaplic.send_event_to_external_gaplic(
            'TOTO',             # gaplic_name
            'sample2',          # gobj_name
            'EV_SET_TIMEOUT',   # event_name
            self,               # subscriber_gobj
            timeout=2,
        )


#===============================================================
#                   GAplic TOTO
#===============================================================
def ac_set_timeout(self, event):
    # TODO: get the seconds
    timeout = event.timeout
    self.set_timeout(timeout)


def ac_timeout(self, event):
    print("Broadcasting EV_MESSAGE")
    self.broadcast_event('EV_MESSAGE')


SAMPLE2_FSM = {
    'event_list': (
        'EV_MESSAGE: top output',
        'EV_TIMEOUT: bottom input',
        'EV_SET_TIMEOUT: top input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_SET_TIMEOUT',  ac_set_timeout,     None),
            ('EV_TIMEOUT',      ac_timeout,         None),
        ),
    }
}

SAMPLE2_GCONFIG = {  # type, default_value, flag, validate_function, desc
}


class Sample2(GObj):
    """  Sample2 GObj.

    .. ginsfsm::
       :fsm: SAMPLE2_FSM
       :gconfig: SAMPLE2_GCONFIG

    *Input-Events:*

        * :attr:`'EV_TIMEOUT'`: .

    *Output-Events:*

        * :attr:`'EV_MESSAGE'`: .

    """
    def __init__(self):
        GObj.__init__(self, SAMPLE2_FSM, SAMPLE2_GCONFIG)
        self.count = 0

    def start_up(self):
        """
        """
        self.timer = self.create_gobj(
            None,
            GTimer,
            self)

    def set_timeout(self, seconds):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=seconds)

    def clear_timeout(self):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=-1)


#===============================================================
#                   Main
#===============================================================
def gaplic1(global_config, **local_conf):
    """ Entry point to run with gserve (PasteDeploy)
    """
    if 'gaplic-name' in local_conf:
        gaplic_name = local_conf.pop('gaplic-name')
    else:
        raise Exception('You must supply an gaplic name ("gaplic-name")')

    ga = GAplic(name=gaplic_name, roles=('titi',), **local_conf)
    ga.create_gobj(
        'sample1',
        Sample1,
        ga,
        __unique_name__=True,
    )
    return ga


def gaplic2(global_config, **local_conf):
    """ Entry point to run with gserve (PasteDeploy)
    """
    if 'gaplic-name' in local_conf:
        gaplic_name = local_conf.pop('gaplic-name')
    else:
        raise Exception('You must supply an gaplic name ("gaplic-name")')

    ga = GAplic(name=gaplic_name, roles=('toto',), **local_conf)
    ga.create_gobj(
        'sample2',
        Sample2,
        ga,
        __unique_name__=True,
    )
    return ga


if __name__ == "__main__":
    """ You can run directly this file, without gserve.
    """
    import logging
    logging.basicConfig(level=logging.DEBUG)
    from ginsfsm.gaplic import setup_gaplic_thread, setup_gaplic_process

    run_as_process = False

    # simulate running from ini file
    local_conf = {
        'gaplic-name': 'TOTO',
        'router_enabled': True,
        'GRouter.server': True,
        'GRouter.trace_router': False,
        'GRouter.localhost_route_ports': 8000,
        'GSock.trace_dump': False,
        'GObj.trace_mach': False,
        'GObj.logger': logging,
    }
    if run_as_process:
        worker = setup_gaplic_process(gaplic2({}, **local_conf))
        worker.start()
    else:
        worker = setup_gaplic_thread(gaplic2({}, **local_conf))
        worker.start()

    # run main process
    local_conf = {
        'gaplic-name': 'TITI',
        'router_enabled': True,
        'GRouter.server': False,
        'GRouter.trace_router': False,
        'GRouter.static_routes': 'TOTO, toto, http://localhost:8000',
        'GSock.trace_dump': False,
        'GObj.trace_mach': False,
        'GObj.logger': logging,
    }
    ga = gaplic1({}, **local_conf)
    try:
        ga.start()
    except (KeyboardInterrupt, SystemExit):

        # stop the gaplic
        worker.stop()

         # wait to finish the other gaplic
        worker.join()

        print('Program stopped')
