"""
gconsole
========

Utility for connect to inside of GAplics

"""

from code import InteractiveInterpreter
import sys
import argparse
import logging
logging.basicConfig(level=logging.INFO)


from ginsfsm.utils import random_key
from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.smachine import SMachine
from ginsfsm.c_timer import GTimer
from ginsfsm.c_sock import GSock
from ginsfsm.utils import hexdump
from ginsfsm.c_stdin import GStdin

my_commands = [
    'help',
    'gaplic',
    'router',
    'set_global_trace',
    'show_routes',
    'add_route',
    'delete_route',
    'show_external_routes',
    'external_command',
    # remember add command help to env_help
]


def ac_rx_data(self, event):
    data = event.kw['data']
    if 0 or self.config.verbose:
        print('Receiving %d bytes' % len(data))
        print(hexdump('<=', data))
    if not data:
        self.stdout.write('\n>>> ')
        self.stdout.flush()
        return

    first_word = data.split()[0]
    if first_word in my_commands:
        command = 'cmd_' + first_word
        if hasattr(self, command):
            cmd = getattr(self, command)
            params = data.split()[1:]
            s = cmd(*params)
            if s:
                self.stdout.write(s)
                self.stdout.flush()
        else:
            self.stdout.write('ERROR: command %r NOT implemented.\n' % command)
    else:
        self.interpreter.runsource(data)

    self.stdout.write('\n>>> ')
    self.stdout.flush()


def ac_timeout(self, event):
    """
    """
    #self.set_timeout(5)


def ac_command_response(self, event):
    """
    """
    #self.set_timeout(5)
    action_return = event.action_return
    self.stdout.write(action_return)
    self.stdout.flush()
    self.stdout.write('\n>>> ')
    self.stdout.flush()


GCONSOLE_FSM = {
    'event_list': (
        'EV_SET_TIMER: bottom output',
        'EV_TIMEOUT:bottom input',
        'EV_RX_DATA:bottom input',
        'EV_COMMAND',
        'EV_SHOW_ROUTES',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',      ac_timeout,             'ST_IDLE'),
            ('EV_RX_DATA',      ac_rx_data,             'ST_IDLE'),
            ('EV_COMMAND',      ac_command_response,    'ST_IDLE'),
            ('EV_SHOW_ROUTES',  ac_command_response,    'ST_IDLE'),
        ),
    }
}


GCONSOLE_GCONFIG = {  # type, default_value, flag, validate_function, desc
    'verbose': [int, 0, 0, None, "Increase output verbosity. Values [0,1,2]"],
}


class GConsole(GObj):
    """  GConsole GObj.

    .. ginsfsm::
       :fsm: GCONSOLE_FSM
       :gconfig: GCONSOLE_GCONFIG

    *Input-Events:*

        * :attr:`'EV_TIMEOUT'`: Timer over.
            Start the machine.

        * :attr:`'EV_RX_DATA'`: Receiving data.
            Receiving data from urls.

    *Output-Events:*

        * :attr:`'EV_START_TIMER'`: Start timer.

    """
    def __init__(self):
        GObj.__init__(self, GCONSOLE_FSM, GCONSOLE_GCONFIG)

    def start_up(self):
        """ Initialization zone."""
        self.stdout = sys.stdout
        self.timer = self.create_gobj(
            None,
            GTimer,
            self,
        )

        if self.config.verbose > 1:
            #TODO: move to local_conf
            settings = {
                'GObj.trace_mach': True,
                'GObj.logger': logging,
            }
            self.overwrite_parameters(-1, **settings)

        self.create_gobj(
            None,
            GStdin,
            self,
        )

        # setup help text for default environment
        env_help = dict()
        env_help['1. help'] = 'Show this help.'
        env_help['2. gaplic'] = 'This gaplic instance.'
        env_help['3. SMachine'] = 'SMachine class.'
        env_help['4. set_global_trace'] = '<bool> Set global trace.'
        env_help['5. show_routes'] = 'Show routes.'
        env_help['6. add_route'] = '<url> (Connect to external gaplic).'
        env_help['7. delete_route'] = '<route_ref> (Remove route).'
        env_help['8. show_external_routes'] = \
            '<route_ref> (Show routes of external gaplic linked by route_ref).'
        env_help['9. external_command'] = \
            '<route_ref> <command> (Execute command in external gaplic linked by route_ref).'

        env = {
            '__name__': "__ginsfsm_console__",
            '__doc__': 'GinsFSM console',
            'gaplic': self.gaplic,
            'SMachine': SMachine,
        }
        self.interpreter = InteractiveInterpreter(locals=env)

        # generate help text
        help = ''
        if env_help:
            help += 'Available commands:'
            for var in sorted(env_help.keys()):
                help += '\n  %-12s %s' % (var, env_help[var])
            help += '\n'
        self.shelp = help

        cprt = 'GinsFSM console.'
        banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)
        banner += '\n\n' + help + '>>> '
        self.stdout.write(banner)
        self.stdout.flush()

        self.set_timeout(1)

    def set_timeout(self, seconds):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=seconds)

    def clear_timeout(self):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=-1)

    def cmd_help(self):
        return self.shelp

    def cmd_gaplic(self):
        return repr(self.gaplic)

    def cmd_set_global_trace(self, value):
        """  parameter always become as strings
        """
        value = eval(value)
        SMachine.global_trace_mach(value)
        GSock.global_trace_dump(value)
        logger = logging.getLogger()
        if value:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    def cmd_show_routes(self):
        router = self.gaplic.router
        ret = self.send_event(
            router,
            'EV_SHOW_ROUTES',
        )
        return ret

    def cmd_add_route(self, url):
        """
        http://localhost:8000/apihost10/__pyramid_router__/websocket
        """
        router = self.gaplic.router
        ret = self.send_event(
            router,
            'EV_ADD_STATIC_ROUTE',
            name=None,
            roles=None,
            urls=url,
        )
        return repr(ret)

    def cmd_delete_route(self, route_ref):
        registry = self.gaplic.router.registry
        route = registry.get_route_by_ref(route_ref)
        if not route:
            return 'Route NOT found'
        if registry.delete_route(route_ref):
            return 'Route deleted'
        return 'Route CANNOT be deleted'

    def cmd_show_external_routes(self, route_ref):
        self.gaplic.router.mt_send_event_to_external_route(
            route_ref,
            'router',
            'EV_SHOW_ROUTES',  # 'EV_COMMAND',
            self.name,
            {
                '__subscribe_response__': True,
            },
        )

    def cmd_external_command(self, route_ref, command):
        self.gaplic.router.mt_send_event_to_external_route(
            route_ref,
            'router',
            'EV_COMMAND',
            self.name,
            {
                '__subscribe_response__': True,
                'command': command,
            },
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        type=int,
        choices=[0, 1, 2],
        default=1,
    )

    local_conf = {
        'router_enabled': True,
        'GRouter.server': True,
        'GRouter.trace_router': True,
        'GWebSocket.trace_mach': False,
        'GSock.trace_dump': False,
        'GObj.trace_mach': False,
        'GObj.logger': logging,
    }
    ga = GAplic(name=random_key(), roles='gcmd',  **local_conf)
    ga.create_gobj(
        'gconsole',
        GConsole,
        ga,
        __unique_name__=True,
    )

    try:
        ga.start()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')


if __name__ == "__main__":
    main()
