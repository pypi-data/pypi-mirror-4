# -*- encoding: utf-8 -*-
""" GWebSocket GObj

Implementation of the WebSocket protocol.

`WebSockets <http://dev.w3.org/html5/websockets/>`_ allow for bidirectional
communication between the browser and server.

.. warning::

   The WebSocket protocol was recently finalized as `RFC 6455
   <http://tools.ietf.org/html/rfc6455>`_ and is not yet supported in
   all browsers.  Refer to http://caniuse.com/websockets for details
   on compatibility.

   This module only supports the latest version 13 of the RFC 6455 protocol.

.. autoclass:: GWebSocket
    :members: start_up

"""
import base64
import array
from os import urandom
import hashlib
import struct
import uuid

from ginsfsm import __version__
from ginsfsm.utils import hexdump
import ginsfsm.escape
from ginsfsm.gconfig import GConfig
from ginsfsm.gmsg import GMsg
from ginsfsm.gobj import GObj
from ginsfsm.c_timer import GTimer
from ginsfsm.compat import (
    bytes_,
)
from ginsfsm.circular_fifo import CircularFIFO
from ginsfsm.buffers import OverflowableBuffer
from ginsfsm.protocols.http.common.parser import (
    HTTPRequestParser,
    HTTPResponseParser,
    build_environment,
)

STRUCT_2BYTES = struct.Struct("!H")
STRUCT_8BYTES = struct.Struct("!Q")
STRUCT_BB = struct.Struct("BB")
STRUCT_BBH = struct.Struct("!BBH")
STRUCT_BBQ = struct.Struct("!BBQ")

OPCODE_CONTINUATION_FRAME = 0x0
OPCODE_TEXT_FRAME = 0x01
OPCODE_BINARY_FRAME = 0x02

OPCODE_CONTROL_CLOSE = 0x08
OPCODE_CONTROL_PING = 0x09
OPCODE_CONTROL_PONG = 0x0A

# websocket supported version.
VERSION = 13

# closing frame status codes.
STATUS_NORMAL = 1000
STATUS_GOING_AWAY = 1001
STATUS_PROTOCOL_ERROR = 1002
STATUS_UNSUPPORTED_DATA_TYPE = 1003
STATUS_STATUS_NOT_AVAILABLE = 1005
STATUS_ABNORMAL_CLOSED = 1006
STATUS_INVALID_PAYLOAD = 1007
STATUS_POLICY_VIOLATION = 1008
STATUS_MESSAGE_TOO_BIG = 1009
STATUS_INVALID_EXTENSION = 1010
STATUS_UNEXPECTED_CONDITION = 1011
STATUS_TLS_HANDSHAKE_ERROR = 1015


def _create_sec_websocket_key():
    uid = uuid.uuid4()
    return base64.encodestring(uid.bytes).strip()


class FrameHead(object):
    """ Websocket frame head.

    This class analize the first two bytes of the header.
    The maximum size of a frame header is 14 bytes.

      0                   1
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
     +-+-+-+-+-------+-+-------------+
     |F|R|R|R| opcode|M| Payload len |
     |I|S|S|S|  (4)  |A|     (7)     |
     |N|V|V|V|       |S|             |
     | |1|2|3|       |K|             |
     +-+-+-+-+-------+-+-------------+

    Full header:

      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +-+-+-+-+-------+-+-------------+-------------------------------+
     |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
     |I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
     |N|V|V|V|       |S|             |   (if payload len==126/127)   |
     | |1|2|3|       |K|             |                               |
     +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
     |     Extended payload length continued, if payload len == 127  |
     + - - - - - - - - - - - - - - - +-------------------------------+
     |                               |Masking-key, if MASK set to 1  |
     +-------------------------------+-------------------------------+
     | Masking-key (continued)       |          Payload Data         |
     +-------------------------------- - - - - - - - - - - - - - - - +
     :                     Payload Data continued ...                :
     + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
     |                     Payload Data continued ...                |
     +---------------------------------------------------------------+
    """

    packer = struct.Struct('BB')

    def __init__(self, circular):
        # Information of the first two bytes header
        self.h_fin = 0  # final fragment in a message
        self.h_reserved_bits = 0
        self.h_opcode = 0
        self.h_mask = 0  # Set to 1 a masking key is present
        self.h_payload_len = 0
        self.circular = circular
        self.busy = False  # in half of header
        self.header_complete = False  # Set True when header is completed
        self.error = False

    def prepare_new_frame(self):
        """Reset variables for a new read.
        """
        # state of frame
        self.busy = True  # in half of header
        self.header_complete = False  # Set True when header is completed
        self.error = False

        # must do
        self.must_read_2_extended_payload_length = False
        self.must_read_8_extended_payload_length = False
        self.must_read_masking_key = False
        self.must_read_payload_data = False

        # information of frame
        self.masking_key = 0
        self.frame_length = 0

    def decode_head(self, data):
        """ READ: Decode the two bytes head.
        """
        if len(data) != 2:
            raise RuntimeError('ERROR decode_ntoh_header needs 2 bytes')
        byte1, byte2 = self.packer.unpack(bytes(data))

        # decod byte1
        self.h_fin = byte1 & 0x80
        self.h_reserved_bits = byte1 & 0x70
        self.h_opcode = byte1 & 0x0f

        # decod byte2
        self.h_mask = byte2 & 0x80
        self.h_payload_len = byte2 & 0x7f

        # analize

        if self.h_mask:
            # must read 4 bytes of masking key
            self.must_read_masking_key = True

        ln = self.h_payload_len
        if ln == 0:
            pass  # no data to read
        else:
            self.must_read_payload_data = True
            if ln < 126:
                # Got all we need to read data
                self.frame_length = self.h_payload_len
            elif ln == 126:
                # must read 2 bytes of extended payload length
                self.must_read_2_extended_payload_length = True
            else:  # ln == 127:
                # must read 8 bytes of extended payload length
                self.must_read_8_extended_payload_length = True

    def decode_extended_length(self, data):
        """ READ: Decode 2/8 bytes of extended payload length.
        """
        if self.must_read_2_extended_payload_length:
            # Read 2 bytes of extended payload length
            if len(data) != 2:
                raise RuntimeError(
                    'ERROR decode_extended_length needs 2 bytes')
            self.frame_length = STRUCT_2BYTES.unpack(bytes(data))[0]
            self.must_read_2_extended_payload_length = False

        elif self.must_read_8_extended_payload_length:
            # Read 8 bytes of extended payload length
            if len(data) != 8:
                raise RuntimeError(
                    'ERROR decode_extended_length needs 8 bytes')
            self.frame_length = STRUCT_8BYTES.unpack(bytes(data))[0]
            self.must_read_8_extended_payload_length = False

    def decode_masking_key(self, data):
        """ READ: Decode the 4 bytes of masking key.
        """
        if len(data) != 4:
            raise RuntimeError('ERROR decode_masking_key needs 4 bytes')
        self.masking_key = data
        self.must_read_masking_key = False

    def consume(self, bf):
        """ Consume input data to get and analyze the frame header.
            Return the consumed size.
        """
        # better work with local variables: more rapid.
        circular = self.circular
        total_consumed = 0
        if not self.busy:
            # waiting the first two byte's head
            available = circular.busy_space + len(bf)
            if available < 2:
                # save the remaining data
                consumed = circular.putdata(bf)
                total_consumed += consumed
                return total_consumed  # wait more data

            needed = 2 - circular.busy_space
            if needed > 0:
                consumed = circular.putdata(bf, needed)
                bf = bf[consumed:]
                total_consumed += consumed

            # we've got enough data! Start a new frame
            self.prepare_new_frame()  # `busy` flag is set.
            data = circular.getdata(2)
            self.decode_head(data)

        # processing extended header
        if self.must_read_2_extended_payload_length:
            available = circular.busy_space + len(bf)
            if available < 2:
                # save the remaining data
                consumed = circular.putdata(bf)
                total_consumed += consumed
                return total_consumed  # wait more data

            needed = 2 - circular.busy_space
            if needed > 0:
                consumed = circular.putdata(bf, needed)
                bf = bf[consumed:]
                total_consumed += consumed

            data = circular.getdata(2)
            self.decode_extended_length(data)  # flag is set.

        if self.must_read_8_extended_payload_length:
            available = circular.busy_space + len(bf)
            if available < 8:
                # save the remaining data
                consumed = circular.putdata(bf)
                total_consumed += consumed
                return total_consumed  # wait more data

            needed = 8 - circular.busy_space
            if needed > 0:
                consumed = circular.putdata(bf, needed)
                bf = bf[consumed:]
                total_consumed += consumed

            data = circular.getdata(8)
            self.decode_extended_length(data)  # flag is set.

        if self.must_read_masking_key:
            available = circular.busy_space + len(bf)
            if available < 4:
                # save the remaining data
                consumed = circular.putdata(bf)
                total_consumed += consumed
                return total_consumed  # wait more data

            needed = 4 - circular.busy_space
            if needed > 0:
                consumed = circular.putdata(bf, needed)
                bf = bf[consumed:]
                total_consumed += consumed

            data = circular.getdata(4)
            self.decode_masking_key(data)  # flag is set

        self.header_complete = True
        return total_consumed

    @property
    def size(self):
        return self.packer.size


def analyze_header(gmsg, iam_server):
    """ Analyze and process the header.
    """
    hd = FrameHead()
    data = gmsg.getdata(hd.size)
    if data is None:
        # there is no enough data
        return hd
    hd.network_to_host(data)
    hd.complete = True
    if hd.h_reserved_bits:
        # client is using as-yet-undefined extensions; abort
        hd.error = True
        gmsg.logger and gmsg.logger.error(
            "ERROR websocket header: using as-yet-undefined h_reserved_bits")
        return hd

    if hd.opcode_is_control:
        #
        #   Control h_opcode
        #
        control = hd.h_opcode
        if control == OPCODE_CONTROL_CLOSE:
            hd.close = True
            pass
        elif control == OPCODE_CONTROL_PING:
            pass
        elif control == OPCODE_CONTROL_PONG:
            pass
        if hd.h_payload_len >= 126:
            # control frames must have payload < 126; abort
            hd.error = True
            gmsg.logger and gmsg.logger.error(
                "ERROR websocket header: too big control frame payloda")
    else:
        #
        #   Data h_opcode
        #
        if iam_server and not hd.h_mask:
            # Unmasked frame; abort
            hd.error = True
            gmsg.logger and gmsg.logger.error(
                "ERROR websocket header: iam_server but unmasked frame")

    return hd


#----------------------------------------------------#
#               Machine Actions
#----------------------------------------------------#
def ac_timeout_waiting_handshake(self, event):
    """ Too much time waiting the handshake.
    """
    self.logger and self.logger.error(
        "ERROR websocket TIMEOUT waiting HANDSHAKE: %r" % self)
    self.on_close_broadcasted = True  # no on_open was broadcasted
    self.close()


def ac_timeout_waiting_frame_header(self, event):
    """ Timeout frame start.
        Too much time waiting the frame header.
    """
    self.start_inactivity_timer(self.config.ping_interval)
    self.ping()


def ac_timeout_waiting_payload_data(self, event):
    """ Timeout frame start.
        Too much time waiting the frame header.
    """
    self.logger and self.logger.error(
        "ERROR websocket TIMEOUT waiting PAYLOAD data")
    self.close()


def ac_connected(self, event):
    """ iam client. send the request
    """
    # send the request and wait the response
    host = self.gsock.host
    port = self.gsock.port
    resource = self.config.resource
    self.do_request(host, port, resource)


def ac_disconnected(self, event):
    """ Partner has disconnected.
    """
    self.closed = True
    self.close()


def ac_process_handshake(self, event):
    """ Process handshake rx data.
    We can be server or client.
    """
    data = event.data
    if self.config.iam_server:
        # analyze the request and response it
        request = self._process_request(data)
        if request:
            self.request = request
            ok = self.do_response()
            if not ok:
                # request refused! Drop connection.
                self.post_event(self.gsock, 'EV_DROP')
                return
            #------------------------------------#
            #   Upgrade to websocket
            #------------------------------------#
            self.set_new_state('ST_WAITING_HEADER')
            self.gaplic.add_callback(self.broadcast_event, 'EV_ON_OPEN')

    else:
        # analyze the response
        response = self._process_response(data)
        if response:
            if response.status == 101:
                #------------------------------------#
                #   Upgrade to websocket
                #------------------------------------#
                self.set_new_state('ST_WAITING_HEADER')
                self.gaplic.add_callback(self.broadcast_event, 'EV_ON_OPEN')
            else:
                self.logger.error(
                    "ERROR websocket Response %d, waiting 101",
                    response.status)
                self.logger.error(hexdump('<==', data))
                self.close()


def ac_process_frame_header(self, event):
    """ Processing the header.
    """
    self.start_inactivity_timer(self.config.ping_interval)
    cur_frame = self.cur_frame
    bf = event.data
    while bf:
        consumed = cur_frame.consume(bf)
        if cur_frame.error:
            self.close()  # on error do break the connection
            return
        bf = bf[consumed:]

        if cur_frame.header_complete:
            if cur_frame.must_read_payload_data:
                # Creat a new buffer for payload data
                self.loaded_data = 0
                self.set_new_state('ST_WAITING_PAYLOAD_DATA')
                self.send_event(self, 'EV_RX_DATA', data=bf)
                return
            else:
                self.frame_completed()


def ac_process_payload_data(self, event):
    """ Get payload data
    """
    bf = event.data
    bf_len = len(bf)
    if bf_len == 0:
        return
    loaded_data = self.loaded_data
    frame_length = self.cur_frame.frame_length
    to_add = frame_length - loaded_data
    if to_add < bf_len:
        # use partial buffer, remain must be another new frame
        data = bf[0:to_add]
        bf = bf[to_add:]
        self.frame_gmsg.putdata(data)
        loaded_data += to_add
    else:
        self.frame_gmsg.putdata(bf)
        loaded_data += bf_len
        bf = None

    self.loaded_data = loaded_data
    if loaded_data == frame_length:
        self.frame_completed()
        self.set_new_state('ST_WAITING_HEADER')
        if bf:
            self.send_event(self, 'EV_RX_DATA', data=bf)


def ac_send_json_message(self, event):
    msg = event.data
    self.send_message(msg)


GWEBSOCKET_FSM = {
    'event_list': (
        'EV_SEND_JSON_MESSAGE: top input',
        'EV_ON_OPEN:top output',
        'EV_ON_CLOSE:top output',
        'EV_ON_MESSAGE:top output',
        'EV_RX_DATA:bottom input',
        # 'EV_TRANSMIT_READY:bottom input',
        'EV_CONNECTED:bottom input',
        'EV_DISCONNECTED:bottom input',
        'EV_SET_TIMER:bottom output',
        'EV_TIMEOUT:bottom input',
    ),
    'state_list': (
        'ST_WAITING_HANDSHAKE',
        'ST_WAITING_HEADER',
        'ST_WAITING_PAYLOAD_DATA',
    ),
    'machine': {
        'ST_WAITING_HANDSHAKE':
        (
            ('EV_CONNECTED',    ac_connected,                       None),
            ('EV_DISCONNECTED', None,                               None),
            ('EV_TIMEOUT',      ac_timeout_waiting_handshake,       None),
            ('EV_RX_DATA',      ac_process_handshake,               None),
        ),

        'ST_WAITING_HEADER':
        (
            ('EV_SEND_JSON_MESSAGE', ac_send_json_message,          None),
            ('EV_DISCONNECTED', ac_disconnected,                    None),
            ('EV_TIMEOUT',      ac_timeout_waiting_frame_header,    None),
            ('EV_RX_DATA',      ac_process_frame_header,            None),
        ),

        'ST_WAITING_PAYLOAD_DATA':
        (
            ('EV_SEND_JSON_MESSAGE', ac_send_json_message,          None),
            ('EV_DISCONNECTED', ac_disconnected,                    None),
            ('EV_TIMEOUT',      ac_timeout_waiting_payload_data,    None),
            ('EV_RX_DATA',      ac_process_payload_data,            None),
        ),
    }
}

GWEBSOCKET_GCONFIG = {
    'gsock': [
        None, None, GConfig.FLAG_DIRECT_ATTR, None, "GSock connection."
    ],
    'request': [
        None, None, GConfig.FLAG_DIRECT_ATTR, None, "websocket request."],
    'iam_server': [bool, True, 0, None, "What side? server or client."],
    'resource': [str, '/', 0, None, "Resource when iam client."],
    'ping_interval': [int, 5*60, 0, None, "Ping interval"],

    # A tempfile should be created if the pending output is larger than
    # outbuf_overflow, which is measured in bytes. The default is 1MB.  This
    # is conservative.
    # It's too used for maximum size of GMsg (buffer for frame payload data)
    'outbuf_overflow': [int, 1048576, 0, None, ""],

    'subscriber': [
        None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
    ],
}


class GWebSocket(GObj):
    """  GWebSocket GObj.
    WebSocket protocol:
    `RFC 6455  <http://tools.ietf.org/html/rfc6455>`_.

    .. ginsfsm::
       :fsm: GWEBSOCKET_FSM
       :gconfig: GWEBSOCKET_GCONFIG

    *Input-Events:*
        * :attr:`'EV_INPUT_EVENT'`: sample input event.

          Event attributes:

              * ``data``: sample event attribute.

    *Output-Events:*
        * :attr:`'EV_OUTPUT_EVENT'`: sample output event.

          Event attributes:

              * ``data``: sample event attribute.

    """

    KEY = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self):
        """ I used Cicular FIFO buffer to save the received data.
            I pull the bytes needed for each operation.
            The buffer is fixed size and by default of 8K bytes,
            and it intend be as rapid as possible.
            It's enough for do analysis of the header.
            The payload data are saved in a OverflowableBuffer buffer,
            a high capacity buffer.
        """
        GObj.__init__(self, GWEBSOCKET_FSM, GWEBSOCKET_GCONFIG)
        self.circular = CircularFIFO(14)  # always the same.
        self.cur_frame = FrameHead(self.circular)  # always the same
        self.closed = False  # channel closed
        self.on_close_broadcasted = False  # event on_close already broadcasted
        self.message_header = None
        self.frame_gmsg = GMsg(1024, self.config.outbuf_overflow, self.logger)
        self.message_buffer = None
        self.parsing_request = None  # A request parser instance
        self.parsing_response = None  # A response parser instance
        self.ginsfsm_user_agent = False  # True when user-agent is ginsfsm
                                    # When user is a browser, it'll be sockjs.
                                    # when user is not browser, at the moment,
                                    # we only recognize ginsfsm websocket.

    def start_up(self):
        """ Initialization zone.
        We always have got the connection done (with gsock)
        because this gobj works:
            * with pyramid web environment
            * or own handshake.

        In own handshake, if iam a client, we initiate the request http.

        """
        if self.config.subscriber:
            self.subscribe_event(None, self.config.subscriber)

        if not self.gsock:
            raise RuntimeError('ERROR websocket needs a gsock done!')

        if self.request:
            # We've got already the request (pyramid environment)
            ok = self.do_response()
            if not ok:
                # request refused! Drop connection.
                self.post_event(self.gsock, 'EV_DROP')
                return
            #------------------------------------#
            #   Upgrade to websocket
            #------------------------------------#
            #   Subscribe all gsock events.
            #------------------------------------#
            self.gsock.delete_all_subscriptions()  # TODO borrando delete http?
            self.gsock.subscribe_event(None, self)
            # TODO: mira interactuar con los timers del canal http.
            self.set_new_state('ST_WAITING_HEADER')
            self.gaplic.add_callback(self.broadcast_event, 'EV_ON_OPEN')

        else:
            #------------------------------------#
            #   Own handshake.
            #   We can be server or client.
            #------------------------------------#
            #   Subscribe all gsock events.
            #------------------------------------#
            self.gsock.delete_all_subscriptions()  # TODO borrando delete http?
            self.gsock.subscribe_event(None, self)

            if self.config.iam_server:
                # wait the request
                pass
            else:
                # send the request and wait the response
                host = self.gsock.read_parameter('host')
                port = self.gsock.read_parameter('port')
                resource = self.read_parameter('resource')
                self.do_request(host, port, resource)

        # Setup the timers
        self.inactivity_timer = self.create_gobj(
            None,
            GTimer,
            self,
            timeout_event_name='EV_TIMEOUT'
        )
        self.start_inactivity_timer(5)

    def go_out(self):
        """ Finish zone.
        """

    def start_inactivity_timer(self, seconds):
        self.send_event(
            self.inactivity_timer,
            'EV_SET_TIMER',
            seconds=seconds
        )

    def stop_inactivity_timer(self):
        self.send_event(
            self.inactivity_timer,
            'EV_SET_TIMER',
            seconds=-1
        )

    def do_request(self, host, port, resource, **options):
        headers = []
        headers.append("GET %s HTTP/1.1" % resource)
        headers.append("User-Agent: ginsfsm-%s" % __version__)
        headers.append("Upgrade: websocket")
        headers.append("Connection: Upgrade")
        if port == 80:
            hostport = host
        else:
            hostport = "%s:%d" % (host, port)
        headers.append("Host: %s" % hostport)

        if "origin" in options:
            headers.append("Origin: %s" % options["origin"])
        else:
            headers.append("Origin: %s" % hostport)

        key = _create_sec_websocket_key()
        headers.append("Sec-WebSocket-Key: %s" % key)
        headers.append("Sec-WebSocket-Version: %s" % VERSION)
        if "header" in options:
            headers.extend(options["header"])

        headers.append("")
        headers.append("")

        header_str = "\r\n".join(headers)
        data = bytes_(header_str)

        self.send_event(self.gsock, 'EV_SEND_DATA', data=data)

    def do_response(self):
        """ Got the request: analyze it and send the response.
        """
        # Websocket only supports GET method
        if self.request.method != "GET":
            data = bytes_(
                "HTTP/1.1 405 Method Not Allowed\r\n"
                "Allow: GET\r\n"
                "Connection: Close\r\n"
                "\r\n"
            )
            self.send_event(self.gsock, 'EV_SEND_DATA', data=data)
            return False

        if hasattr(self.request, 'environ'):
            environ = self.request.environ
        else:
            environ = build_environment(self.request, '', '', '')

        user_agent = environ.get("HTTP_USER_AGENT", "").lower()
        ln = len("ginsfsm")
        if len(user_agent) >= ln:
            if user_agent[0:ln] == "ginsfsm":
                self.ginsfsm_user_agent = True

        # Upgrade header should be present and should be equal to WebSocket
        if environ.get("HTTP_UPGRADE", "").lower() != "websocket":
            data = bytes_(
                "HTTP/1.1 400 Bad Request\r\n"
                "Connection: Close\r\n"
                "\r\n"
                "Can \"Upgrade\" only to \"WebSocket\"."
            )
            self.send_event(self.gsock, 'EV_SEND_DATA', data=data)
            return False

        # Connection header should be upgrade.
        # Some proxy servers/load balancers
        # might mess with it.
        connection = list(
            map(
                lambda s: s.strip().lower(),
                environ.get("HTTP_CONNECTION", "").split(",")
            )
        )
        if "upgrade" not in connection:
            data = bytes_(
                "HTTP/1.1 400 Bad Request\r\n"
                "Connection: Close\r\n"
                "\r\n"
                "\"Connection\" must be \"Upgrade\"."
            )
            self.send_event(self.gsock, 'EV_SEND_DATA', data=data)
            return False

        # The difference between version 8 and 13 is that in 8 the
        # client sends a "Sec-Websocket-Origin" header and in 13 it's
        # simply "Origin".
        supported_version = ("7", "8", "13")
        if not environ.get(
                "HTTP_SEC_WEBSOCKET_VERSION") in supported_version:
            data = bytes_(
                "HTTP/1.1 426 Upgrade Required\r\n"
                "Sec-WebSocket-Version: 13\r\n\r\n"
            )
            self.send_event(self.gsock, 'EV_SEND_DATA', data=data)
            return False

        fields = (
            "HTTP_HOST",
            "HTTP_SEC_WEBSOCKET_KEY",
            "HTTP_SEC_WEBSOCKET_VERSION"
        )
        if not all(list(map(lambda f: environ.get(f), fields))):
            data = bytes_(
                "HTTP/1.1 400 Bad Request\r\n"
                "Connection: Close\r\n"
                "\r\n"
                "Missing/Invalid WebSocket headers."
            )
            self.send_event(self.gsock, 'EV_SEND_DATA', data=data)
            return False

        key = environ.get("HTTP_SEC_WEBSOCKET_KEY", None)
        if not key or len(base64.b64decode(bytes_(key))) != 16:
            data = bytes_(
                "HTTP/1.1 400 Bad Request\r\n"
                "Connection: Close\r\n"
                "\r\n"
                "Sec-Websocket-Key is invalid key."
            )
            # TODO: review
            #self.send_event(self.gsock, 'EV_SEND_DATA', data=data)
            #return False

        #------------------------------#
        #   Accept the connection
        #------------------------------#
        subprotocol_header = ''
        subprotocols = environ.get("HTTP_SEC_WEBSOCKET_PROTOCOL", '')
        subprotocols = [s.strip() for s in subprotocols.split(',')]
        if subprotocols:
            selected = self.select_subprotocol(subprotocols)
            if selected:
                assert selected in subprotocols
                subprotocol_header = "Sec-WebSocket-Protocol: %s\r\n" % (
                    selected)

        data = bytes_(
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Accept: %s\r\n"
            "%s"
            "\r\n" % (
                self._challenge_response(key),
                subprotocol_header)
        )
        self.send_event(self.gsock, 'EV_SEND_DATA', data=data)

        return True

    @staticmethod
    def compute_accept_value(key):
        """Computes the value for the Sec-WebSocket-Accept header,
        given the value for Sec-WebSocket-Key.
        """
        sha1 = hashlib.sha1()
        sha1.update(bytes_(key))
        sha1.update(b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11")  # Magic value
        return ginsfsm.escape.native_str(base64.b64encode(sha1.digest()))

    def _challenge_response(self, key):
        return GWebSocket.compute_accept_value(key)

    def select_subprotocol(self, subprotocols):
        """Invoked when a new WebSocket requests specific subprotocols.

        ``subprotocols`` is a list of strings identifying the
        subprotocols proposed by the client.  This method may be
        overridden to return one of those strings to select it, or
        ``None`` to not select a subprotocol.  Failure to select a
        subprotocol does not automatically abort the connection,
        although clients may close the connection if none of their
        proposed subprotocols was selected.
        """
        return None

    def close(self):
        if not self.closed:
            self.closed = True
            self.send_close()
            self.gaplic.add_callback(self.send_event, self.gsock, 'EV_DROP')

        if not self.on_close_broadcasted:
            self.on_close_broadcasted = True
            self.gaplic.add_callback(self.broadcast_event, 'EV_ON_CLOSE')

        self.set_new_state('ST_WAITING_HANDSHAKE')

    def frame_completed(self):
        """ Process the completed frame.
        """
        cur_frame = self.cur_frame
        gmsg = self.frame_gmsg
        gmsg.reset_rd()

        unmasked = None
        if cur_frame.frame_length:
            ln = gmsg.bytesleft()
            unmasked = gmsg.getdata(ln)
            if cur_frame.h_mask:
                h_mask = cur_frame.masking_key
                for i in range(ln):
                    unmasked[i] = unmasked[i] ^ h_mask[i % 4]

        if cur_frame.h_fin:
            # last frame of message
            if self.message_buffer:
                self.message_buffer.append(unmasked)
                message = self.message_buffer.get()
                operation = self.message_header.h_opcode
            else:
                message = unmasked
                operation = cur_frame.h_opcode

            if operation == OPCODE_CONTINUATION_FRAME:
                self.logger.error("%r: Websocket CONTINUATION FRAME" % (self))
            elif operation == OPCODE_TEXT_FRAME:
                if message:
                    try:
                        message = message.decode("utf-8")
                    except:
                        pass
                    if self.trace_mach:
                        self.logger.debug(
                            "%r: RECEIVE Websocket text FRAME: %r" % (
                            self, message)
                        )
                    self.gaplic.add_callback(
                        self.broadcast_event,
                        'EV_ON_MESSAGE',
                        data=message
                    )
            elif operation == OPCODE_BINARY_FRAME:
                if message:
                    if self.trace_mach:
                        self.logger.debug(
                            "%r: RECEIVE Websocket binary FRAME: %r" % (
                            self, message)
                        )
                    self.gaplic.add_callback(
                        self.broadcast_event,
                        'EV_ON_MESSAGE',
                        data=unmasked
                    )
            elif operation == OPCODE_CONTROL_CLOSE:
                self.close()
            elif operation == OPCODE_CONTROL_PING:
                if self.trace_mach:
                    self.logger.debug("%r: RECEIVE Websocket Control PING" % (
                        self)
                    )
                self.pong()
            elif operation == OPCODE_CONTROL_PONG:
                if self.trace_mach:
                    self.logger.debug("%r: RECEIVE Websocket Control PONG" % (
                        self)
                    )
            else:
                self.logger.error("ERROR %r: Websocket BAD OPCODE %r" % (
                    self, operation)
                )

            self.message_header = None
            self.message_buffer = None

        else:
            # Message with several frames
            if not self.message_header:
                self.message_header = cur_frame
            if not self.message_buffer:
                self.message_buffer = OverflowableBuffer(
                    self.config.outbuf_overflow)
            self.message_buffer.append(unmasked)

        gmsg.reset_wr()  # Reset buffer for next frame
        cur_frame.busy = False

    def ping(self):
        self._write_frame(True, OPCODE_CONTROL_PING, '')

    def pong(self):
        self._write_frame(True, OPCODE_CONTROL_PONG, '')

    def send_close(self, status=STATUS_NORMAL, reason=''):
        if status < 0 or status > 0xFFFF:
            raise ValueError("code is invalid range")
        self._write_frame(
            True,
            OPCODE_CONTROL_CLOSE,
            STRUCT_2BYTES.pack(status) + bytes_(reason)
        )

    def send(self, message, binary=False):
        """ Send message to the client.
            Api websocket.
        """
        if isinstance(message, dict):
            message = ginsfsm.escape.json_encode(message)

        self.write_message(message, binary)

    def send_message(self, msg):
        """ Send jsonfied message compatible with sockjs.

        Compatible with sockjs protocol.
        """
        msg = ginsfsm.escape.json_encode(msg)
        self.write_message('a[%s]' % msg)

    def send_jsonfied_message(self, msg):
        """ Send jsonfied message. Not sockjs compatible.
        """
        msg = ginsfsm.escape.json_encode(msg)
        self.write_message(msg)

    def write_message(self, message, binary=False):
        """Sends the given message to the client of this Web Socket."""
        if binary:
            h_opcode = 0x2
        else:
            h_opcode = 0x1
        message = bytes_(message, "utf-8")
        self._write_frame(True, h_opcode, message)

    def _write_frame(self, h_fin, h_opcode, data):
        if h_fin:
            byte1 = h_opcode | 0x80
        else:
            byte1 = h_opcode

        ln = len(data)

        if ln < 126:
            byte2 = ln
            if not self.config.iam_server:
                byte2 |= 0x80
            frame = STRUCT_BB.pack(byte1, byte2)
        elif ln <= 0xFFFF:
            byte2 = 126
            if not self.config.iam_server:
                byte2 |= 0x80
            frame = STRUCT_BBH.pack(byte1, byte2, ln)

        elif ln <= 0xFFFFFFFF:
            byte2 = 127
            if not self.config.iam_server:
                byte2 |= 0x80
            frame = STRUCT_BBQ.pack(byte1, byte2, ln)

        else:
            raise ValueError("data is too long")

        if not self.config.iam_server:
            mask_key = urandom(4)
            #s = self.mask(mask_key, data)
            #data = mask_key + b"".join(s)
            data = mask_key + self.mask(mask_key, data)

        frame += data
        self.send_event(self.gsock, 'EV_SEND_DATA', data=frame)

    def mask(self, mask_key, data):
        """
        mask or unmask data. Just do xor for each byte

        mask_key: 4 byte string(byte).

        data: data to mask/unmask.
        """
        _m = array.array("B", mask_key)
        _d = array.array("B", data)
        for i in range(len(_d)):
            _d[i] ^= _m[i % 4]
        return _d.tostring()

    def _process_request(self, data):
        new_request = None
        cur_request = self.parsing_request
        while data:
            if cur_request is None:
                cur_request = HTTPRequestParser()
            n = cur_request.received(data)

            if cur_request.completed:
                # The cur_request (with the body) is ready to use.
                self.parsing_request = None
                new_request = cur_request
                cur_request = None
            else:
                self.parsing_request = cur_request
            if n >= len(data):
                break
            data = data[n:]

        return new_request

    def _process_response(self, data):
        new_response = None
        cur_response = self.parsing_response
        while data:
            if cur_response is None:
                cur_response = HTTPResponseParser()
            n = cur_response.received(data)

            if cur_response.completed:
                self.parsing_response = None
                new_response = cur_response
                cur_response = None
            else:
                self.parsing_response = cur_response
            if n >= len(data):
                break
            data = data[n:]

        return new_response
