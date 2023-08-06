# -*- encoding: utf-8 -*-
""" GSockjsServer GObj

.. autoclass:: GSockjsServer
    :members: start_up

"""

from pyramid.security import (
    Allow,
    Everyone,
    DENY_ALL,
)

from ginsfsm.gobj import GObj
from ginsfsm.protocols.sockjs.server.c_static import (
    GInfo,
    GIFrame,
)
from ginsfsm.protocols.sockjs.server.c_transport_websocket import GRawWebsocket
from ginsfsm.protocols.sockjs.server import session, sessioncontainer
from ginsfsm.protocols.sockjs.server import stats
from ginsfsm.protocols.sockjs.server.c_session import GSockjsSession
from ginsfsm.protocols.sockjs.server import proto


#-------------------------------------------#
#               Actions
#-------------------------------------------#
def ac_timeout(self, event):
    self.counter += 1
    self.send_event(self.timer, 'EV_SET_TIMER', seconds=self.seconds)


def ac_sample(self, event):
    """ Event attributes:
        * :attr:`data`: example.

    """
    self.broadcast_event('EV_OUTPUT_EVENT', data=event.data)


GSOCKJSSERVER_FSM = {
    'event_list': (
        'EV_INPUT_EVENT:top input',
        'EV_OUTPUT_EVENT:top output',
    ),
    'state_list': (
        'ST_IDLE',
    ),
    'machine': {
        'ST_IDLE':
        (
            ('EV_INPUT_EVENT',      ac_sample,      None),
        ),
    }
}

GSOCKJSSERVER_GCONFIG = {
    'subscriber': [
        None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
    ],
    'sockjs_app_class': [
        None, None, 0, None,
        "Class to receive sockjs events."
        "GSockjsServer will create a instance of this class."
    ],

    # like tornado settings
    'session_check_interval': [
        int, 1, 0, None, "Sessions check interval in seconds"
    ],
    'disconnect_delay': [
        int, 5, 0, None, "Session expiration in seconds"
    ],
    'heartbeat_delay': [
        int, 25, 0, None,
        "Heartbeat time in seconds. Do not change this value unless "
        "you absolutely sure that new value will work."
    ],
    'disabled_transports': [tuple, (), 0, None, "Transports disabled"],
    'sockjs_url': [
        str, 'http://cdn.sockjs.org/sockjs-0.3.min.js', 0, None,
        "SockJS location"
    ],
    'response_limit': [int, 128 * 1024, 0, None, "Max response body size"],
    'jsessionid': [
        bool, True, 0, None,
        "Enable or disable JSESSIONID cookie handling"
    ],
    'immediate_flush': [
        bool, True, 0, None,
        "Should sockjs-tornado flush messages immediately or queue then and"
        " flush on next ioloop tick"
    ],
    'verify_ip': [
        bool, True, 0, None,
        "Enable IP checks for polling transports. If enabled, "
        "all subsequent polling calls should be from the same IP address."
    ],
    'per_user': [
        bool, False, 0, None,
        "TODO: default is True in pyramid_sockjs"
    ],
}


class GSockjsServer(GObj):
    """  GSockjsServer GObj.
    This gobj only works
    with `Pyramid <http://www.pylonsproject.org/>`_ framework.

    .. ginsfsm::
       :fsm: GSOCKJSSERVER_FSM
       :gconfig: GSOCKJSSERVER_GCONFIG

    *Input-Events:*
        * :attr:`'EV_INPUT_EVENT'`: sample input event.

          Event attributes:

              * ``data``: sample event attribute.

    *Output-Events:*
        * :attr:`'EV_OUTPUT_EVENT'`: sample output event.

          Event attributes:

              * ``data``: sample event attribute.

    """
    __acl__ = [
        (Allow, Everyone, 'view'),
        (DENY_ALL),
    ]

    def __init__(self):
        GObj.__init__(self, GSOCKJSSERVER_FSM, GSOCKJSSERVER_GCONFIG)
        # Store connection class

    def start_up(self):
        """ Initialization zone.
        """
        if self.config.subscriber is None:
            self.config.subscriber = self.parent
        self.subscribe_event(None, self.config.subscriber)

        if not self.config.sockjs_app_class:
            raise Exception('You must supply a connection application.')
        self._connection = self.config.sockjs_app_class

        #----------------------------------------------#
        #           Static handlers
        #----------------------------------------------#

        # Info
        self.create_gobj(
            'info',
            GInfo,
            self,
            sockjs_server=self,
        )
        # IFrame
        self.create_gobj(
            'iframe',
            GIFrame,
            self,
            re_name='iframe[0-9-.a-z_]*.html',
            sockjs_server=self,
        )
        # RawWebsocket
        self.create_gobj(
            'websocket',
            GRawWebsocket,
            self,
            sockjs_server=self,
        )

        #----------------------------------------------#
        #           Session URLs
        #----------------------------------------------#
        self.sockjs_session = self.create_gobj(
            'sockjs_session',
            GSockjsSession,
            self,
            re_name='^[^/.]+$',
            sockjs_server=self,
        )

        #----------------------------------------------#
        #           Setup
        #----------------------------------------------#
        # Store connection class
        #self._connection = connection

        # Initialize io_loop
        #self.io_loop = io_loop or ioloop.IOLoop.instance()

        disabled_transports = self.config.disabled_transports
        self.websockets_enabled = 'websocket' not in disabled_transports
        self.cookie_needed = self.config.jsessionid

        # Sessions
        self._sessions = sessioncontainer.SessionContainer()

        #check_interval = self.settings['session_check_interval'] * 1000
        #self._sessions_cleanup =ioloop.PeriodicCallback(self._sessions.expire,
        #                                                 check_interval,
        #                                                 self.io_loop)
        #self._sessions_cleanup.start()

        # Stats
        self.stats = stats.StatsCollector()

    def create_session(self, session_id, register=True):
        """Creates new session object and returns it.

        `request`
            Request that created the session. Will be used to get query string
            parameters and cookies
        `register`
            Should be session registered in a storage. Websockets don't
            need it.
        """
        # TODO: Possible optimization here for settings.get
        s = session.Session(
            self._connection,
            self,
            session_id,
            self.config.disconnect_delay
        )
        self.logger.debug("CREATE SESSION: id=%s, s=%r" % (session_id, s,))
        if register:
            self._sessions.add(s)

        return s

    def get_session(self, session_id):
        """Get session by session id

        `session_id`
            Session id
        """
        s = self._sessions.get(session_id)
        self.logger.debug("GET SESSION: id=%s, s=%r" % (session_id, s,))
        return s

    def get_connection_class(self):
        """Return associated connection class"""
        return self._connection

    # Broadcast helper
    def broadcast(self, clients, msg):
        """Optimized `broadcast` implementation.
        Depending on type of the session, will json-encode
        message once and will call either `send_message` or `send_jsonifed`.

        `clients`
            Clients iterable
        `msg`
            Message to send
        """
        json_msg = None

        count = 0

        for c in clients:
            sess = c.session
            if not sess.is_closed:
                if sess.send_expects_json:
                    if json_msg is None:
                        json_msg = proto.json_encode(msg)
                    sess.send_jsonified(json_msg, False)
                else:
                    sess.send_message(msg, stats=False)

                count += 1

        self.stats.on_pack_sent(count)


#----------------------------------------------------------------#
#                   Views
#----------------------------------------------------------------#
from ginsfsm.protocols.sockjs.server.basehandler import BaseHandler
from pyramid.view import view_config


@view_config(
    context=GSockjsServer,
    name='',
    attr='get',
    request_method='GET',
)
class GreetingsHandler(BaseHandler):
    """SockJS greetings page handler"""
    def get(self):
        response = self.response
        self.enable_cache()
        response.content_type = 'text/plain'
        response.charset = 'UTF-8'
        data = 'Welcome to SockJS!\n'.encode()
        response.body = data
        return response
