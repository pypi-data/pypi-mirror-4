# -*- coding: utf-8 -*-
"""
    Sockjs Websocket transport implementation
"""
import logging

from pyramid.view import view_config

from ginsfsm.protocols.sockjs.server.proto import json_decode
from ginsfsm.gobj import GObj
from ginsfsm.gconfig import GConfig
from ginsfsm.protocols.sockjs.server.c_websocket import GWebSocket
from ginsfsm.protocols.sockjs.server.session import BaseSession
from ginsfsm.protocols.sockjs.server.session import ConnectionInfo
from ginsfsm.protocols.wsgi.webob.websocket_response import WebsocketResponse
from ginsfsm.deferred import Deferred
from ginsfsm.utils import hexdump
from ginsfsm.protocols.sockjs.server.util import bytes_to_str


#----------------------------------------------------------------#
#                   WebSocketHandler
#----------------------------------------------------------------#
class WebSocketHandler(object):
    """ Mixin to adapt GWebSocket and Sockjs session handler
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.channel = channel = request.environ['ginsfsm.channel']
        self.gsock = channel.gsock

    def get_conn_info(self):
        """Return `ConnectionInfo` object from current transport"""
        return ConnectionInfo(
            self.request.remote_addr,  # remote_ip
            self.request.cookies,
            self.request.params,  # arguments
            self.request.headers,
            self.request.path
        )

    def _execute(self):
        #
        #   Accept the connection
        #
        self.ws_connection = self.context.gaplic.create_gobj(
            'websocket',
            GWebSocket,
            self.channel,     # child of parent, to be delete when channel was
            request=self.request,
            gsock=self.gsock,
        )
        self.ws_connection.delete_all_subscriptions()
        # da error al suscribir, no es un gobj, como hago para las callback?
        deferred_open = Deferred(0, self.open)
        deferred_message = Deferred(0, self.on_message)
        deferred_close = Deferred(0, self.on_close)
        self.ws_connection.subscribe_event('EV_ON_OPEN', deferred_open)
        self.ws_connection.subscribe_event('EV_ON_MESSAGE', deferred_message)
        self.ws_connection.subscribe_event('EV_ON_CLOSE', deferred_close)

        #
        #   This will execute ResponseInterrupt.
        #   Now Pyramid has nothing to do.
        #   All server/client dialog will be done by GWebSocket.
        #
        response = WebsocketResponse(self.context, self.request)
        return response

    def write_message(self, message, binary=False):
        """Sends the given message to the client of this Web Socket."""
        if self.ws_connection.ginsfsm_user_agent:
            self.ws_connection.send_jsonfied_message(message)
        else:
            self.ws_connection.write_message(message, binary)

    def close(self):
        self.gsock.mt_drop()

#----------------------------------------------------------------#
#                   GWebsocket GClass
#                   /*/*/websocket
#----------------------------------------------------------------#
GWEBSOCKET_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GWebsocket(GObj):
    """  GWebsocket GObj.
    """
    def __init__(self):
        GObj.__init__(self, {}, GWEBSOCKET_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """


#----------------------------------------------------------------#
#                   GWebsocket Views
#                   /*/*/websocket
#----------------------------------------------------------------#
@view_config(
    context=GWebsocket,
    name='',
    attr='execute',
)
class WebsocketTransport(WebSocketHandler):
    name = 'websocket'

    def __init__(self, context, request):
        super(WebsocketTransport, self).__init__(
            context,
            request,
        )
        self.session = None
        self.active = True

    def execute(self):
        self.sid = self.context.parent.re_matched_name
        response = self._execute()
        return response

    def open(self, event):
        # Handle session
        self.session = self.context.sockjs_server.create_session(
            self.sid,
            register=False
        )

        if not self.session.set_handler(self):
            self.close()
            return

        self.session.verify_state()

        if self.session:
            self.session.flush()

    def _detach(self):
        if self.session is not None:
            self.session.remove_handler(self)
            self.session = None

    def on_message(self, event):
        message = event.data
        # SockJS requires that empty messages should be ignored
        if not message or not self.session:
            return

        try:
            msg = json_decode(bytes_to_str(message))  # ? v1.0.0

        except Exception:
            logging.exception(
                'ERROR WebSocket json_decode, gobj %r, msg %s' %
                (self, hexdump('<==', message)))
            # Close running connection
            self.gsock.mt_drop()
            return

        try:
            if isinstance(msg, list):
                self.session.on_messages(msg)
            else:
                self.session.on_messages((msg,))
        except Exception:
            logging.exception(
                'ERROR WebSocket on_messages, gobj %r, msg %s' %
                (self, hexdump('<==', message)))
            # Close running connection
            self.gsock.mt_drop()

    def on_close(self, event):
        # Close session if websocket connection was closed
        if self.session is not None:
            # Detach before closing session
            session = self.session
            self._detach()
            session.close()

    def send_pack(self, message, binary=False):
        # Send message
        try:
            self.write_message(message, binary)
        except IOError:
            logging.exception(
                "ERROR WebsocketTransport send_pack")
            self.context.gaplic.add_callback(self.on_close)

    def session_closed(self):
        # If session was closed by the application, terminate websocket
        # connection as well.
        try:
            self.close()
        except IOError:
            pass
        finally:
            self._detach()

    def auto_decode(self):
        return False


#----------------------------------------------------------------#
#                   RawWebsocket Session
#----------------------------------------------------------------#
class RawSession(BaseSession):
    """ Raw session without any sockjs protocol encoding/decoding.
        Simply works as a proxy between `SockJSConnection` class
        and `RawWebSocketTransport`.
    """
    def send_message(self, msg, stats=True, binary=False):
        self.handler.send_pack(msg, binary)

    def on_message(self, msg):
        self.conn.on_message(msg)


#----------------------------------------------------------------#
#                   GRawWebsocket GClass
#                   /websocket
#----------------------------------------------------------------#
GRAWWEBSOCKET_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GRawWebsocket(GObj):
    """  GRawWebsocket GObj.
    """
    def __init__(self):
        GObj.__init__(self, {}, GRAWWEBSOCKET_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """


#----------------------------------------------------------------#
#                   GRawWebsocket Views
#                   /websocket
#----------------------------------------------------------------#
@view_config(
    context=GRawWebsocket,
    name='',
    attr='execute',
)
class RawWebsocketTransport(WebSocketHandler):
    name = 'rawwebsocket'

    def __init__(self, context, request):
        super(RawWebsocketTransport, self).__init__(
            context,
            request,
        )
        self.session = None
        self.active = True

    def execute(self):
        #self.sid = self.context.parent.re_matched_name
        response = self._execute()
        return response

    def open(self, event):
        # Create and attach to session
        self.session = RawSession(
            self.context.sockjs_server.get_connection_class(),
            self.context.sockjs_server
        )
        if not self.session.set_handler(self):
            self.close()
            return
        self.session.verify_state()

    def _detach(self):
        if self.session is not None:
            self.session.remove_handler(self)
            self.session = None

    def on_message(self, event):
        message = event.data
        # SockJS requires that empty messages should be ignored
        if not message or not self.session:
            return

        try:
            self.session.on_message(message)
        except Exception:
            logging.exception('ERROR RawWebSocket')

            # Close running connection
            # self._detach() ? v1.0.0
            self.gsock.mt_drop()

    def on_close(self, event):
        # Close session if websocket connection was closed
        if self.session is not None:
            # Detach before closing session
            session = self.session
            self._detach()
            session.close()

    def send_pack(self, message, binary=False):
        # Send message
        try:
            self.write_message(message, binary)
        except IOError:
            logging.exception(
                "ERROR RawWebsocketTransport send_pack")
            self.context.gaplic.add_callback(self.on_close)

    def session_closed(self):
        # If session was closed by the application, terminate websocket
        # connection as well.
        try:
            self.close()
        except IOError:
            pass
        finally:
            self._detach()
