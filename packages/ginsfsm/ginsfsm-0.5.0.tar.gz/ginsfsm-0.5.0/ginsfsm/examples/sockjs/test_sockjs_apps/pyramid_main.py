# -*- encoding: utf-8 -*-
"""
applic
======

TestApps

"""
from pyramid.security import (
    Allow,
    Everyone,
    ALL_PERMISSIONS,
)

from ginsfsm.gobj import GObj
from ginsfsm.c_timer import GTimer
from ginsfsm.protocols.sockjs.server.c_sockjs_server import GSockjsServer

from .test import (
    EchoConnection,
    CloseConnection,
    TickerConnection,
    AmplifyConnection,
    BroadcastConnection,
    CookieEcho,
)

#----------------------------------------------------------------------#
#                           TestApps
#----------------------------------------------------------------------#
TESTAPPS_FSM = {}

TESTAPPS_GCONFIG = {
}


class TestSocksjsApps(GObj):
    """  Root resource for TestApps.

    .. ginsfsm::
       :fsm: TESTAPPS_FSM
       :gconfig: TESTAPPS_GCONFIG

    *Input-Events:*
        * :attr:`'EV_TIMEOUT'`: Timer over.

    """
    __acl__ = [
        (Allow, Everyone, ALL_PERMISSIONS)
    ]

    def __init__(self):
        GObj.__init__(self, TESTAPPS_FSM, TESTAPPS_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """

        self.timer = self.create_gobj(
            None,       # unnamed gobj
            GTimer,     # gclass
            self        # parent
        )
        #self.send_event(self.timer, 'EV_SET_TIMER', seconds=self.seconds)

        # create test sockjs apps
        self.echo = self.create_gobj(
            'echo',         # named gobj
            GSockjsServer,  # gclass
            self,           # parent
            sockjs_app_class=EchoConnection,
            response_limit=4096,
        )
        self.disabled_websocket_echo = self.create_gobj(
            'disabled_websocket_echo',
            GSockjsServer,
            self,
            sockjs_app_class=EchoConnection,
            disabled_transports=['websocket'],
        )
        self.disabled_websocket_echo = self.create_gobj(
            'close',
            GSockjsServer,
            self,
            sockjs_app_class=CloseConnection,
        )
        self.disabled_websocket_echo = self.create_gobj(
            'ticker',
            GSockjsServer,
            self,
            sockjs_app_class=TickerConnection,
        )
        self.disabled_websocket_echo = self.create_gobj(
            'amplify',
            GSockjsServer,
            self,
            sockjs_app_class=AmplifyConnection,
        )
        self.disabled_websocket_echo = self.create_gobj(
            'cookie_needed_echo',
            GSockjsServer,
            self,
            sockjs_app_class=CookieEcho,
        )
        self.disabled_websocket_echo = self.create_gobj(
            'broadcast',
            GSockjsServer,
            self,
            sockjs_app_class=BroadcastConnection,
        )
