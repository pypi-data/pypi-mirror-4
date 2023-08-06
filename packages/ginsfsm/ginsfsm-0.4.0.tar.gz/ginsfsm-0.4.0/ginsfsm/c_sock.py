# -*- encoding: utf-8 -*-
"""
GObj :class:`GSock`
===================

GObj for manage socket events.

.. autoclass:: GSock
    :members: start_up, get_next_dst

"""

# ======================================================================
#   Code inspired in asyncore.py, waitress and tornado.
# ======================================================================

try:
    import ssl  # Python 2.6+
except ImportError:
    ssl = None

import select
import socket
import time
import errno
import logging
import sys
import warnings
import os

from ginsfsm.gobj import GObj
from ginsfsm.utils import hexdump
from ginsfsm.buffers import (
    ReadOnlyFileBasedBuffer,
    OverflowableBuffer,
)
from errno import (
    EALREADY,
    EINPROGRESS,
    EWOULDBLOCK,
    ECONNRESET,
    EINVAL,
    ENOTCONN,
    ESHUTDOWN,
#    EINTR,
    EISCONN,
    EBADF,
    ECONNABORTED,
    EAGAIN,
#    EADDRNOTAVAIL,
    errorcode
    )

_DISCONNECTED = frozenset((
    ECONNRESET,
    ENOTCONN,
    ESHUTDOWN,
    ECONNABORTED,
))


class IOLoop(object):
    # Constants from the epoll module
    _EPOLLIN = 0x001
    _EPOLLPRI = 0x002
    _EPOLLOUT = 0x004
    _EPOLLERR = 0x008
    _EPOLLHUP = 0x010
    _EPOLLRDHUP = 0x2000
    _EPOLLONESHOT = (1 << 30)
    _EPOLLET = (1 << 31)

    # Our events map exactly to the epoll events
    NONE = 0
    READ = _EPOLLIN
    WRITE = _EPOLLOUT
    ERROR = _EPOLLERR | _EPOLLHUP | _EPOLLRDHUP


def _strerror(err):
    try:
        return os.strerror(err)
    except (ValueError, OverflowError, NameError):
        if err in errorcode:
            return errorcode[err]
        return "Unknown error %s" % err

_reraised_exceptions = (
    KeyboardInterrupt,
    SystemExit,
    )


def readwrite(obj, flags):
    try:
        if flags & (IOLoop.ERROR):
            obj.handle_close()
            return
        if flags & (IOLoop.READ):
            obj.handle_read_event()
        if flags & (IOLoop.WRITE):
            obj.handle_write_event()
    except socket.error as e:
        if e.args[0] not in (
                EBADF,
                ECONNRESET,
                ENOTCONN,
                ESHUTDOWN,
                ECONNABORTED):
            obj.handle_error()
        else:
            obj.handle_close()
    except _reraised_exceptions:
        close_all_sockets(obj._socket_map)
        raise
    except:
        #obj.handle_error() #TODO
        raise


def poll_loop(socket_map, _impl, timeout):
    """ check poll, return True if some sock event, otherwise False.
    """
    ret = False
    try:
        event_pairs = _impl.poll(timeout)
    except Exception as e:
        # Depending on python version and IOLoop implementation,
        # different exception types may be thrown and there are
        # two ways EINTR might be signaled:
        # * e.errno == errno.EINTR
        # * e.args is like (errno.EINTR, 'Interrupted system call')
        if (getattr(e, 'errno', None) == errno.EINTR or
                (isinstance(getattr(e, 'args', None), tuple) and
                len(e.args) == 2 and e.args[0] == errno.EINTR)):
            return ret
        else:
            raise
    #print "events ------------->", event_pairs
    #print "sockmp ------------->", socket_map.keys()
    for fd, events in event_pairs:
        obj = socket_map.get(fd, None)
        if obj is None:
            continue
        ret = True
        readwrite(obj, events)
    return ret


#===========================================================
#       GSock gobj
#===========================================================
def ac_connect(self, event):
    self._mt_connect(**event.kw)


def ac_drop(self, event):
    self._mt_drop()


def ac_send_data(self, event):
    """ Write in the output data buffer and flush it right now.
    """
    self._write_soon(event.data)
    self._transmit_ready_event_done = False
    self._send_some()


def ac_write_output_data(self, event):
    """ Write in the output data buffer.
        Equivalent to waitress' write_soon().
    """
    self._write_soon(event.data)


def ac_flush_output_data(self, event):
    """ Flush the output data buffer.
        Equivalent to waitress' send_some().
    """
    self._transmit_ready_event_done = False
    self._send_some()


GSOCK_FSM = {
    'event_list': (
        'EV_CONNECT:top input',
        'EV_DROP:top input',
        'EV_CONNECTED: top output',
        'EV_DISCONNECTED: top output',
        'EV_RX_DATA: top output',
        'EV_SEND_DATA: top input',
        'EV_WRITE_OUTPUT_DATA: top input',
        'EV_FLUSH_OUTPUT_DATA: top input',
        'EV_TRANSMIT_READY: top output'
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_CONNECT',              ac_connect,             None),
            ('EV_DROP',                 ac_drop,                None),
            ('EV_SEND_DATA',            ac_send_data,           None),
            ('EV_WRITE_OUTPUT_DATA',    ac_write_output_data,   None),
            ('EV_FLUSH_OUTPUT_DATA',    ac_flush_output_data,   None),
        ),
    }
}

GSOCK_GCONFIG = {
    'subscriber': [None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
        ],
    'trace_dump': [bool, False, 0, None, "trace tx/rx messages"],
    'ip': [str, '', 0, None, ""],
    'host': [str, '', 0, None, "server or client host (ip or name)"],
    'port': [int, 0, 0, None, "server or client port"],
    'ssl_options': [dict, {}, 0, None, "ssl options"],
    'tx_buffer_size': [int, 4096, 0, None, ""],
    'connected_event_name': [str, 'EV_CONNECTED', 0, None,
        "Must be empty if you don't want receive this event"],
    'disconnected_event_name': [str, 'EV_DISCONNECTED', 0, None,
        "Must be empty if you don't want receive this event"],
    'transmit_ready_event_name': [str, 'EV_TRANSMIT_READY', 0, None,
        "Must be empty if you don't want receive this event"],
    'rx_data_event_name': [str, 'EV_RX_DATA', 0, None, ""],
    '_socket_map': [None, {}, 0, None, "Set by gaplic. Dict {fd:Gobj}"],
    '_impl_poll': [None, None, 0, None, "Set by gaplic. epoll implementation"],

    # send_bytes is the number of bytes to send to socket.send().  Multiples
    # of 9000 should avoid partly-filled packets, but don't set this larger
    # than the TCP write buffer size.  In Linux, /proc/sys/net/ipv4/tcp_wmem
    # controls the minimum, default, and maximum sizes of TCP write buffers.
    'send_bytes': [int, 18000, 0, None, ""],

    # A tempfile should be created if the pending output is larger than
    # outbuf_overflow, which is measured in bytes. The default is 1MB.  This
    # is conservative.
    'outbuf_overflow': [int, 1048576, 0, None, ""],
    'close_when_flushed': [bool, False, 0, None,
        "True to close the socket when flushed"],
}


class GSock(GObj):
    """  Client socket gobj.

    Manage socket events.

    .. ginsfsm::
       :fsm: GSOCK_FSM
       :gconfig: GSOCK_GCONFIG


    *Input-Events:*
        * :attr:`'EV_SEND_DATA'`:

          Write data in the output data buffer and flush it right now.

          Equivalent to EV_WRITE_OUTPUT_DATA and EV_FLUSH_OUTPUT_DATA together.

          Event attributes:

            * ``data``: data to send.

        * :attr:`'EV_WRITE_OUTPUT_DATA'`:

          Write data in the output data buffer.

          Event attributes:

            * ``data``: data to send.

        * :attr:`'EV_FLUSH_OUTPUT_DATA'`:

          Flush the output buffer data.



    *Output-Events:*
        * :attr:`'EV_CONNECTED'`: socket connected.

          Attributes added to the sent :term:`event`:

            * ``peername``: remote address to which the socket is connected.
            * ``sockname``: the socket’s own address.

        * :attr:`'EV_DISCONNECTED'`: socket disconnected.

        * :attr:`'EV_TRANSMIT_READY'`: socket ready to transmit more data.

        * :attr:`'EV_RX_DATA'`: data received.

          The data is not buffered.
          As much data are read by recv() as data are broadcast.

          Event attributes:

            * ``data``: Data received from remote address.
    """
    _global_trace_dump = False

    def __init__(self):
        GObj.__init__(self, GSOCK_FSM, GSOCK_GCONFIG)

        self.txed_msgs = 0  # TODO:  estos alarmas/estadisticas
        self.rxed_msgs = 0
        self.txed_bytes = 0
        self.rxed_bytes = 0
        self.__trace_dump = False

        self.connected = False
        self.addr = None        # dont't make private: waitress use it.
        self.socket = None      # dont't make private: waitress use it.
        self.sockname = None

        self._socket_map = {}   # socket_map set by gaplic. Dict {fd:Gobj}
        self._impl_poll = None  # _poll(),epoll() implementation
        self._accepting = False
        self._transmit_ready_event_done = False
        self._clisrv = False
        self._fileno = None
        self.last_activity = 0  # Time of last activity
        self.will_close = False  # set to True to close the socket.
        # TODO: WARNING! outbufs directly used by c_http_clisrv!!
        self.outbufs = [OverflowableBuffer(self.outbuf_overflow)]

    def start_up(self):
        """ Initialization zone.

        Subcribe all enabled :term:`output-event`'s to ``subscriber``.
        By default the subscriber is the parent.
        ::

            if self.subscriber is None:
                self.subscriber = self.parent
            self.subscribe_event(None, self.subscriber)
        """
        if self.subscriber is None:
            self.subscriber = self.parent
        self.subscribe_event(None, self.subscriber)

        # Verify the SSL options. Otherwise we don't get errors until clients
        # connect. This doesn't verify that the keys are legitimate, but
        # the SSL module doesn't do that until there is a connected socket
        # which seems like too much work
        if self.ssl_options:
            # Only certfile is required: it can contain both keys
            if 'certfile' not in self.ssl_options:
                raise KeyError('missing key "certfile" in ssl_options')

            if not os.path.exists(self.ssl_options['certfile']):
                raise ValueError('certfile "%s" does not exist' %
                    self.ssl_options['certfile'])
            if ('keyfile' in self.ssl_options and
                    not os.path.exists(self.ssl_options['keyfile'])):
                raise ValueError('keyfile "%s" does not exist' %
                    self.ssl_options['keyfile'])

    def set_clisrv_socket(self, sock):
        # Set to nonblocking just to make sure for cases where we
        # get a socket from a blocking source.
        sock.setblocking(0)
        self.add_socket(sock)
        self.connected = True
        self._clisrv = True
        # The constructor no longer requires that the socket
        # passed be connected.
        try:
            self.addr = sock.getpeername()
        except socket.error as err:
            if err.args[0] == ENOTCONN:
                # To handle the case where we got an unconnected
                # socket.
                self.connected = False
            else:
                # The socket is broken in some unknown way, alert
                # the user and remove it from the socket_map (to prevent
                # polling of broken sockets).
                self.remove_socket()
                raise
        self.sockname = self.socket.getsockname()

    def __repr__(self):
        status = [self.__class__.__module__ + "." + self.__class__.__name__]
        if self._accepting and self.addr:
            status.append('listening')
        elif self.connected:
            status.append('connected')
        if self.addr is not None:
            try:
                status.append('%s:%d' % self.addr)
            except TypeError:
                status.append(repr(self.addr))
        return '<%s at %#x>' % (' '.join(status), id(self))

    __str__ = __repr__

    def create_socket(self, family, xtype):
        self.family_and_type = family, xtype
        sock = socket.socket(family, xtype)
        sock.setblocking(0)
        self.add_socket(sock)

    def set_reuse_addr(self):
        # try to re-use a server port if possible
        try:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
                )
        except socket.error:
            pass

    def add_socket(self, sock):
        self.socket = sock
        self._fileno = sock.fileno()
        self._socket_map[self._fileno] = self
        self._impl_poll.register(
            self._fileno, IOLoop.WRITE | IOLoop.READ | IOLoop.ERROR)

    def remove_socket(self):
        fd = self._fileno
        self._socket_map.pop(fd, None)
        self._fileno = None
        self.socket = None
        try:
            self._impl_poll.unregister(fd)
        except (OSError, IOError):
            logging.error("Error deleting fd from IOLoop", exc_info=True)

    #==================================================
    #   socket object methods.
    #==================================================
    def listen(self, num):
        self._accepting = True
        if os.name == 'nt' and num > 5:
            num = 5
        return self.socket.listen(num)

    def bind(self, addr):
        self.addr = addr
        return self.socket.bind(addr)

    def connect(self, address):
        self.connected = False
        err = self.socket.connect_ex(address)
        if err in (EINPROGRESS, EALREADY, EWOULDBLOCK, ) \
        or err == EINVAL and os.name in ('nt', 'ce'):
            return
        if err in (0, EISCONN):
            self.addr = address
            self.handle_connect_event()
        else:
            raise socket.error(err, errorcode[err])

    def accept(self):
        # XXX can return either an address pair or None
        try:
            conn, addr = self.socket.accept()
        except TypeError:
            return None
        except socket.error as why:
            if why.args[0] in (EWOULDBLOCK, ECONNABORTED):
                return None
            else:
                raise
        else:
            return conn, addr

    def send(self, data):
        try:
            result = self.socket.send(data)
            if result == 0:
                # With OpenSSL, if we couldn't write the entire buffer,
                # the very same string object must be used on the
                # next call to send.  Therefore we suppress
                # merging the write buffer after an incomplete send.
                # A cleaner solution would be to set
                # SSL_MODE_ACCEPT_MOVING_WRITE_BUFFER, but this is
                # not yet accessible from python
                # (http://bugs.python.org/issue8240)
                pass
            return result
        except socket.error as why:
            if why.args[0] == EWOULDBLOCK:
                return 0
            elif why.args[0] in _DISCONNECTED:
                self.handle_close()
                return 0
            else:
                raise

    def recv(self):
        try:
            data = self.socket.recv(8192)
            if not data:
                # a closed connection is indicated by signaling
                # a read condition, and having recv() return 0.
                self.handle_close()
                return b''
            else:
                return data
        except socket.error as why:
            # winsock sometimes throws ENOTCONN
            if why.args[0] in _DISCONNECTED:
                self.handle_close()
                return b''
            else:
                raise

    def close(self):
        self.connected = False
        self._accepting = False
        if self.socket:
            try:
                self.socket.close()
            except socket.error as why:
                if why.args[0] not in (ENOTCONN, EBADF):
                    raise

    # cheap inheritance, used to pass all other attribute
    # references to the underlying socket object.
    def __getattr__(self, attr):
        try:
            retattr = getattr(self.socket, attr)
        except AttributeError:
            raise AttributeError("%s instance has no attribute '%s'"
                                 % (self.__class__.__name__, attr))
        else:
            msg = "%(me)s.%(attr)s is deprecated; use %(me)s.socket.%(attr)s "\
                "instead" % {'me': self.__class__.__name__, 'attr': attr}
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return retattr

    def handle_read_event(self):
        logging.debug("handle_read_event    (%s %s)" % (self, self.name))
        if self._accepting:
            # _accepting sockets are never connected, they "spawn" new
            # sockets that are connected
            self.handle_accept()
        elif not self.connected:
            self.handle_connect_event()
            self.handle_read()
        else:
            self.handle_read()

    def handle_connect_event(self):
        logging.debug("handle_connect_event (%s %s)" % (self, self.name))
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            raise socket.error(err, _strerror(err))
        self.connected = True
        self.handle_connect()

    def handle_write_event(self):
        logging.debug("handle_write_event   (%s %s)" % (self, self.name))
        if self._accepting:
            # Accepting sockets shouldn't get a write event.
            # We will pretend it didn't happen.
            return

        if not self.connected:
            #check for errors
            err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if err != 0:
                raise socket.error(err, _strerror(err))

            self.handle_connect_event()
        self.handle_write()

    def handle_error(self):
        nil, t, v, tbinfo = compact_traceback()

        # sometimes a user repr method will crash.
        try:
            self_repr = repr(self)
        except:
            self_repr = '<__repr__(self) failed for object at %0x>' % id(self)

        logging.error(
            'uncaptured python exception, closing channel %s (%s:%s %s)' % (
                self_repr,
                t,
                v,
                tbinfo
                )
            )
        self.handle_close()

    #====================================================
    #   Mine's
    #====================================================
    def handle_accept(self):
        try:
            pair = self.accept()
            if pair is not None:
                self.handle_accepted(*pair)

        except socket.error:
            # Linux: On rare occasions we get a bogus socket back from
            # accept. socketmodule.c:makesockaddr complains that the
            # address family is unknown. We don't want the whole server
            # to shut down because of this.
            logging.warning('server accept() threw an exception',
                exc_info=True)

    def handle_accepted(self, sock, addr):
        sock.close()
        logging.warning('unhandled accepted event')

    def _mt_connect(self, **kw):
        """ Try to connect to (host, port).

        :param kw: valid keyword arguments are ``host`` and ``port``.

        This method calls to :meth:`get_next_dst` to get the destination tuple.

        Example::

            # override host,port attributes
            mt_connect(host='127.0.0.1', port=80)

        Or::

            # use current host,port attributes
            mt_connect()

        :class:`GSock` will broadcast some of ``'EV_CONNECTED'`` or
        ``'EV_DISCONNECTED'`` event as result of this action.
        """
        self.__dict__.update(**kw)

        if self.connected:
            logging.error(
                "ERROR connecting to host '%s', port %s. "
                "ALREADY CONNECTED." % (self.host, self.port))
            return False
        if self.socket:
            logging.error(
                "ERROR connecting to host '%s', port %s. SOCKET EXISTS." %
                (self.host, self.port))
            self.close()  # ???
            self.remove_socket()  # ???
            #TODO: si cumple el timeout de conexion viene por aqui
            #return False ???

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host, self.port = self.get_next_dst()
        try:
            self.ip = ip = socket.gethostbyname(self.host)
        except Exception as e:
            logging.error('ERROR gethostbyname %s' % e)
            return False
        logging.info("%s ==> Connecting to host '%s', ip '%s', port %s..." % (
            self.name, self.host, ip, self.port))
        try:
            self.connect((ip, self.port))
        except Exception as e:
            logging.error("_mt_connect() ERROR %s" % repr(e))
            return False
        return True

    def get_next_dst(self):
        """ Supply the destination ``(host,port)`` tuple to
        :meth:`_mt_connect` method.
        By default this function returns the internal ``(host,port)``
        attributes.

        TO BE OVERRIDE if you need other policy.
        """
        return (self.host, self.port)

    def handle_connect(self):
        data = {}
        data['peername'] = self.socket.getpeername()
        self.sockname = data['sockname'] = self.socket.getsockname()
        logging.info("%s <== Connected! %s host '%s'" % (
            self.name,
            "FROM" if self._clisrv else "TO",
            str(data['peername'])))
        # remove WRITE
        self._impl_poll.modify(self._fileno, IOLoop.READ | IOLoop.ERROR)
        if self.connected_event_name is not None:
            self.broadcast_event(self.connected_event_name, **data)

    def _mt_drop(self):
        """ Drop the connexion.
        """
        logging.info(
            "%s ==> Disconnecting from host '%s', ip '%s', port %s..." % (
            self.name, self.host, self.ip, self.port))
        if self.socket:
            self.socket.shutdown(socket.SHUT_RDWR)
            self._impl_poll.modify(
                self._fileno, IOLoop.WRITE | IOLoop.READ | IOLoop.ERROR)
        else:
            self.close()
        return 0

    def handle_close(self):
        for outbuf in self.outbufs:
            try:
                outbuf._close()
            except:
                logging.exception(
                    'Unknown exception while trying to close outbuf')
        self.close()
        self.remove_socket()
        if 0:
            logging.info(
                "%s <== Disconnected! from host '%s', port %s" % (
                self.name, self.host, self.port))
        #TODO: pon la causa del disconnect
        if self.disconnected_event_name is not None:
            self.broadcast_event(self.disconnected_event_name)

    def handle_read(self):
        try:
            data = self.recv()
        except socket.error:
            self.handle_error()
            return

        ln = len(data)
        self.rxed_msgs += 1
        self.rxed_bytes += ln
        if self.trace_dump:
            logging.debug(
                "Recv data '%s' (%d bytes)\n%s" % (
                    self.name, ln, hexdump('<=', data)))

        if self.rx_data_event_name is not None:
            self.broadcast_event(self.rx_data_event_name, data=data)

    def readable(self):
        #"predicate for inclusion in the readable for select()"
        return True

    #-------------------------------------------------#
    #               Write zone
    #-------------------------------------------------#
    def any_outbuf_has_data(self):
        for outbuf in self.outbufs:
            if bool(outbuf):
                return True
        return False

    def writable(self):
        #"predicate for inclusion in the writable for select()"
        return self.any_outbuf_has_data() or \
            (not self.connected) or \
            self.will_close

    def _mt_send_data(self, data):
        """ Send data.
        :param data: data to send.
        """

    def _write_soon(self, data):
        """ Write data in the output buffer.
        """
        if data:
            if data.__class__ is ReadOnlyFileBasedBuffer:
                # they used wsgi.file_wrapper
                self.outbufs.append(data)
                nextbuf = OverflowableBuffer(self.outbuf_overflow)
                self.outbufs.append(nextbuf)
            else:
                self.outbufs[-1].append(data)
            return len(data)
        return 0

    def handle_write(self):
        # Precondition: there's data in the out buffer to be sent, or
        # there's a pending will_close request
        if not self.connected:
            # we dont want to close the channel twice
            return

        something_sent = self._send_some()
        if not self.connected:
            # can be disconnected after _send_some()
            return
        if not something_sent:
            if not self._transmit_ready_event_done:
                self._transmit_ready_event_done = True
                if self.transmit_ready_event_name is not None:
                    self.broadcast_event(self.transmit_ready_event_name)

    def _send_some(self):
        """ Send as much output data as possible.
        """
        sent = False
        try:
            sent = self._flush_some()
        except socket.error:
            logging.exception('Socket error')
            self.will_close = True
        except:
            self.logger.exception('Unexpected exception when flushing')
            self.will_close = True

        if self.close_when_flushed and not self.any_outbuf_has_data():
            self.close_when_flushed = False
            self.will_close = True

        if self.will_close:
            self.handle_close()
        return sent

    def _flush_some(self):
        # Send as much data as possible to our client
        sent = 0
        dobreak = False

        while True:
            outbuf = self.outbufs[0]
            outbuflen = len(outbuf)
            if outbuflen <= 0:
                # self.outbufs[-1] must always be a writable outbuf
                if len(self.outbufs) > 1:
                    toclose = self.outbufs.pop(0)
                    try:
                        toclose._close()
                    except:
                        self.logger.exception(
                            'Unexpected error when closing an outbuf')
                    continue  # pragma: no cover (coverage bug, it is hit)
                else:
                    dobreak = True

            while outbuflen > 0:
                chunk = outbuf.get(self.send_bytes)
                if self.trace_dump:
                    logging.info(
                        "Send data '%s' (%d bytes)\n%s" %
                        (self.name, len(chunk), hexdump('=>', chunk)))
                num_sent = self.send(chunk)
                if num_sent:
                    outbuf.skip(num_sent, True)
                    outbuflen -= num_sent
                    sent += num_sent
                else:
                    dobreak = True
                    break

            if dobreak:
                break

        if sent:
            self.last_activity = time.time()
            return True

        return False

    #-------------------------------------------------#
    #               trace zone
    #-------------------------------------------------#
    @property
    def trace_dump(self):
        return self.__trace_dump or self._global_trace_dump

    @trace_dump.setter
    def trace_dump(self, value):
        """  Enable/Disable dump trace.
        """
        self.__trace_dump = value


class GSSLSock(GSock):
    """A GSock class to write to and read from a non-blocking SSL socket.

    If the socket passed to the constructor is already connected,
    it should be wrapped with::

        ssl.wrap_socket(sock, do_handshake_on_connect=False, **kwargs)

    Unconnected sockets will be wrapped when connect is finished.
    """

    def __init__(self):
        GSock.__init__(self)

    def start_up(self):
        """ Initialization zone.
        """
        self._ssl_accepting = True
        self._handshake_reading = False
        self._handshake_writing = False
        self._ssl_connect_callback = None

    def writable(self):
        #"predicate for inclusion in the writable for select()"
        return self._handshake_reading or super(GSSLSock, self).reading()

    def readable(self):
        #"predicate for inclusion in the readable for select()"
        return self._handshake_writing or super(GSSLSock, self).writing()

    def _do_ssl_handshake(self):
        # Based on code from test_ssl.py in the python stdlib
        try:
            self._handshake_reading = False
            self._handshake_writing = False
            self.socket.do_handshake()
        except ssl.SSLError, err:
            if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                self._handshake_reading = True
                return
            elif err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                self._handshake_writing = True
                return
            elif err.args[0] in (ssl.SSL_ERROR_EOF,
                                 ssl.SSL_ERROR_ZERO_RETURN):
                return self.close()
            elif err.args[0] == ssl.SSL_ERROR_SSL:
                try:
                    peer = self.socket.getpeername()
                except:
                    peer = '(not connected)'
                logging.warning("SSL Error on %d %s: %s",
                                self.socket.fileno(), peer, err)
                return self.close()
            raise
        except socket.error, err:
            if err.args[0] in (errno.ECONNABORTED, errno.ECONNRESET):
                return self.close()
        else:
            self._ssl_accepting = False
            if self._ssl_connect_callback is not None:
                callback = self._ssl_connect_callback
                self._ssl_connect_callback = None
                self._run_callback(callback)

    def handle_read(self):
        if self._ssl_accepting:
            self._do_ssl_handshake()
            return
        super(GSSLSock, self).handle_read()

    def handle_write(self):
        if self._ssl_accepting:
            self._do_ssl_handshake()
            return
        super(GSSLSock, self).handle_write()

    def handle_connect(self):
        # When the connection is complete, wrap the socket for SSL
        # traffic.  Note that we do this by overriding _handle_connect
        # instead of by passing a callback to super().connect because
        # user callbacks are enqueued asynchronously on the IOLoop,
        # but since _handle_events calls _handle_connect immediately
        # followed by _handle_write we need this to be synchronous.
        self.socket = ssl.wrap_socket(self.socket,
                                      do_handshake_on_connect=False,
                                      **self.ssl_options)
        super(GSSLSock, self).handle_connect()

    # TODO para revisar

    def recv(self):
        """ TODO: pending to include
        while True:
            # Read from the socket until we get EWOULDBLOCK or equivalent.
            # SSL sockets do some internal buffering, and if the data is
            # sitting in the SSL object's buffer select() and friends
            # can't see it; the only way to find out if it's there is to
            # try to read it.
            if not super(GSSLSock, self).recv():
                break
        """

        if self._ssl_accepting:
            # If the handshake hasn't finished yet, there can't be anything
            # to read (attempting to read may or may not raise an exception
            # depending on the SSL version)
            return b''

        try:
            # SSLSocket objects have both a read() and recv() method,
            # while regular sockets only have recv().
            # The recv() method blocks (at least in python 2.6) if it is
            # called when there is nothing to read, so we have to use
            # read() instead.
            data = self.socket.read(8192)
            if not data:
                # a closed connection is indicated by signaling
                # a read condition, and having recv() return 0.
                self.handle_close()
                return b''
            else:
                return data
        except ssl.SSLError as why:
            # SSLError is a subclass of socket.error, so this except
            # block must come first.
            if why.args[0] == ssl.SSL_ERROR_WANT_READ:
                return b''
            else:
                raise
        except socket.error as why:
            # winsock sometimes throws ENOTCONN
            if why.args[0] in _DISCONNECTED:
                self.handle_close()
                return b''
            elif why.args[0] in (EWOULDBLOCK, EAGAIN):
                return b''
            else:
                raise


# ---------------------------------------------------------------------------
# used for debugging.
# ---------------------------------------------------------------------------
def compact_traceback():
    t, v, tb = sys.exc_info()
    tbinfo = []
    if not tb:  # Must have a traceback
        raise AssertionError("traceback does not exist")
    while tb:
        tbinfo.append((
            tb.tb_frame.f_code.co_filename,
            tb.tb_frame.f_code.co_name,
            str(tb.tb_lineno)
            ))
        tb = tb.tb_next

    # just to be safe
    del tb

    file, function, line = tbinfo[-1]
    info = ' '.join(['[%s|%s|%s]' % x for x in tbinfo])
    return (file, function, line), t, v, info


def close_all_sockets(socket_map, ignore_all=False):
    for x in list(socket_map.values()):
        try:
            x.close()
        except OSError as x:
            if x.args[0] == EBADF:
                pass
            elif not ignore_all:
                raise
        except _reraised_exceptions:
            raise
        except:
            if not ignore_all:
                raise
    socket_map.clear()


#================================================================
#   Poll implementations.
#   Code copied from tornado/ioloop.py
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#================================================================
class _EPoll(object):
    """An epoll-based event loop using our C module for Python 2.5 systems"""
    _EPOLL_CTL_ADD = 1
    _EPOLL_CTL_DEL = 2
    _EPOLL_CTL_MOD = 3

    def __init__(self):
        self._epoll_fd = epoll.epoll_create()

    def fileno(self):
        return self._epoll_fd

    def close(self):
        os.close(self._epoll_fd)

    def register(self, fd, events):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_ADD, fd, events)

    def modify(self, fd, events):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_MOD, fd, events)

    def unregister(self, fd):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_DEL, fd, 0)

    def poll(self, timeout):
        return epoll.epoll_wait(self._epoll_fd, int(timeout * 1000))


class _KQueue(object):
    """A kqueue-based event loop for BSD/Mac systems."""
    def __init__(self):
        self._kqueue = select.kqueue()
        self._active = {}

    def fileno(self):
        return self._kqueue.fileno()

    def close(self):
        self._kqueue.close()

    def register(self, fd, events):
        if fd in self._active:
            raise IOError("fd %d already registered" % fd)
        self._control(fd, events, select.KQ_EV_ADD)
        self._active[fd] = events

    def modify(self, fd, events):
        self.unregister(fd)
        self.register(fd, events)

    def unregister(self, fd):
        events = self._active.pop(fd)
        self._control(fd, events, select.KQ_EV_DELETE)

    def _control(self, fd, events, flags):
        kevents = []
        if events & IOLoop.WRITE:
            kevents.append(select.kevent(
                    fd, filter=select.KQ_FILTER_WRITE, flags=flags))
        if events & IOLoop.READ or not kevents:
            # Always read when there is not a write
            kevents.append(select.kevent(
                    fd, filter=select.KQ_FILTER_READ, flags=flags))
        # Even though control() takes a list, it seems to return EINVAL
        # on Mac OS X (10.6) when there is more than one event in the list.
        for kevent in kevents:
            self._kqueue.control([kevent], 0)

    def poll(self, timeout):
        kevents = self._kqueue.control(None, 1000, timeout)
        events = {}
        for kevent in kevents:
            fd = kevent.ident
            if kevent.filter == select.KQ_FILTER_READ:
                events[fd] = events.get(fd, 0) | IOLoop.READ
            if kevent.filter == select.KQ_FILTER_WRITE:
                if kevent.flags & select.KQ_EV_EOF:
                    # If an asynchronous connection is refused, kqueue
                    # returns a write event with the EOF flag set.
                    # Turn this into an error for consistency with the
                    # other IOLoop implementations.
                    # Note that for read events, EOF may be returned before
                    # all data has been consumed from the socket buffer,
                    # so we only check for EOF on write events.
                    events[fd] = IOLoop.ERROR
                else:
                    events[fd] = events.get(fd, 0) | IOLoop.WRITE
            if kevent.flags & select.KQ_EV_ERROR:
                events[fd] = events.get(fd, 0) | IOLoop.ERROR
        return events.items()


class _Select(object):
    """A simple, select()-based IOLoop implementation for non-Linux systems"""
    def __init__(self):
        self.read_fds = set()
        self.write_fds = set()
        self.error_fds = set()
        self.fd_sets = (self.read_fds, self.write_fds, self.error_fds)

    def close(self):
        pass

    def register(self, fd, events):
        if fd in self.read_fds or fd in self.write_fds or fd in self.error_fds:
            raise IOError("fd %d already registered" % fd)
        if events & IOLoop.READ:
            self.read_fds.add(fd)
        if events & IOLoop.WRITE:
            self.write_fds.add(fd)
        if events & IOLoop.ERROR:
            self.error_fds.add(fd)
            # Closed connections are reported as errors by epoll and kqueue,
            # but as zero-byte reads by select, so when errors are requested
            # we need to listen for both read and error.
            self.read_fds.add(fd)

    def modify(self, fd, events):
        self.unregister(fd)
        self.register(fd, events)

    def unregister(self, fd):
        self.read_fds.discard(fd)
        self.write_fds.discard(fd)
        self.error_fds.discard(fd)

    def poll(self, timeout):
        readable, writeable, errors = select.select(
            self.read_fds, self.write_fds, self.error_fds, timeout)
        events = {}
        for fd in readable:
            events[fd] = events.get(fd, 0) | IOLoop.READ
        for fd in writeable:
            events[fd] = events.get(fd, 0) | IOLoop.WRITE
        for fd in errors:
            events[fd] = events.get(fd, 0) | IOLoop.ERROR
        return events.items()

#================================================================
#   Choose a poll implementation. Use epoll if it is available,
#   fall back to select() for non-Linux platforms
#================================================================
if hasattr(select, "epoll"):
    # Python 2.6+ on Linux
    _poll = select.epoll
elif hasattr(select, "kqueue"):
    # Python 2.6+ on BSD or Mac
    _poll = _KQueue
else:
    try:
        # Linux systems with our C module installed
        from ginsfsm import epoll
        _poll = _EPoll
    except Exception:
        # All other systems
        if "linux" in sys.platform:
            logging.warning("epoll module not found; using select()")
        _poll = _Select
