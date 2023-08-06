# -*- encoding: utf-8 -*-
"""
    SockJS session implementation.

    All transport urls come with /{server_id}/{session_id} subpath.

    The :class:GSockjsSession and :class:GSessionId classes
    captures these segments.

"""
from ginsfsm.gobj import GObj
from ginsfsm.gconfig import GConfig
from ginsfsm.protocols.sockjs.server.c_transport_xhr import (
    GXhrSend,
    GXhrPolling,
    GXhrStreaming,
)
from ginsfsm.protocols.sockjs.server.c_transport_jsonp import (
    GJsonpSend,
    GJsonpPolling,
)
from ginsfsm.protocols.sockjs.server.c_transport_eventsource import (
    GEventsourceStreaming,
)
from ginsfsm.protocols.sockjs.server.c_transport_htmlfile import (
    GHtmlfileStreaming,
)
from ginsfsm.protocols.sockjs.server.c_transport_websocket import (
    GWebsocket,
)


#----------------------------------------------------------------#
#                   GSockjsSession GClass
#----------------------------------------------------------------#
GSOCKJSSESSION_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GSockjsSession(GObj):
    """  GSockjsSession GObj aka GServerID.
    This gobj treats the {server_id} segment of the url.
    The main reason for this segment is to make it easier
    to configure load balancer
    and enable sticky sessions based on first part of the url.
    The sockjs serve must ignore it.

    This gobj would be called GServerID instead of GSockjsSession.
    We don't name this gobj as GServerID for a better understanding of the
    parent gobj view point.
    """
    def __init__(self):
        GObj.__init__(self, {}, GSOCKJSSESSION_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """
        self.session_id = self.create_gobj(
            'session_id',
            GSessionId,
            self,
            re_name='^[^/.]+$',
            sockjs_server=self.sockjs_server,
        )

#----------------------------------------------------------------#
#                   GSessionId GClass
#----------------------------------------------------------------#
GSESSIONID_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GSessionId(GObj):
    """  GSessionId GObj.
    """
    def __init__(self):
        GObj.__init__(self, {}, GSESSIONID_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """
        #-------------------------------------------#
        #           Global handlers
        #               /xhr_send
        #               /jsonp_send
        #-------------------------------------------#
        self.create_gobj(
            'xhr_send',
            GXhrSend,
            self,
            sockjs_server=self.sockjs_server,
        )
        self.create_gobj(
            'jsonp_send',
            GJsonpSend,
            self,
            sockjs_server=self.sockjs_server,
        )

        #-------------------------------------------#
        #           Transports
        #               /websocket
        #               /xhr
        #               /xhr_streaming
        #               /jsonp
        #               /eventsource
        #               /htmlfile
        #-------------------------------------------#
        self.create_gobj(
            'websocket',
            GWebsocket,
            self,
            sockjs_server=self.sockjs_server,
        )
        self.create_gobj(
            'xhr',
            GXhrPolling,
            self,
            sockjs_server=self.sockjs_server,
        )
        self.create_gobj(
            'xhr_streaming',
            GXhrStreaming,
            self,
            sockjs_server=self.sockjs_server,
        )
        self.create_gobj(
            'jsonp',
            GJsonpPolling,
            self,
            sockjs_server=self.sockjs_server,
        )
        self.create_gobj(
            'eventsource',
            GEventsourceStreaming,
            self,
            sockjs_server=self.sockjs_server,
        )
        self.create_gobj(
            'htmlfile',
            GHtmlfileStreaming,
            self,
            sockjs_server=self.sockjs_server,
        )
