# -*- encoding: utf-8 -*-
"""
GAplic
======

Container of gobjs.

:class:`GAplic` supplies the main loop in a thread o subprocess context.

:class:`GAplic` has the next methods:

* :meth:`GAplic.create_gobj`
* :meth:`GAplic.destroy_gobj`
* :meth:`GAplic.find_unique_gobj`
* :meth:`GAplic.send_event_to_external_gaplic`
* :meth:`GAplic.send_event_to_external_role`
* :meth:`GAplic.subscribe_event_from_external_gaplic`
* :meth:`GAplic.subscribe_event_from_external_role`
* :meth:`GAplic.unsubscribe_event_from_external_gaplic`
* :meth:`GAplic.unsubscribe_event_from_external_role`
* :meth:`GAplic.add_callback`
* :meth:`GAplic.start`
* :meth:`GAplic.stop`
* :meth:`GAplic.mt_subprocess`


A gaplic can run in a thread or subprocess context,
always with the same interface.

Auxiliary functions:
====================

To run a :class:`GAplic` instance like a **thread**:
:func:`setup_gaplic_thread`.

To run a :class:`GAplic` instance like a **subprocess**:
:func:`setup_gaplic_process`.

To use configuration file .ini
with `PasteDeploy <http://pythonpaste.org/deploy>`_ in composite mode:
:func:`gaplic_factory`.


GAplic class
============

.. autoclass:: GAplic
    :members: create_gobj, destroy_gobj,
        find_unique_gobj,
        send_event_to_external_gaplic,
        send_event_to_external_role,
        subscribe_event_from_external_gaplic,
        subscribe_event_from_external_role,
        unsubscribe_event_from_external_gaplic,
        unsubscribe_event_from_external_role,
        add_callback,
        start,
        stop,
        mt_subprocess


Thead context
=============

Running as thread::

    ga = GAplic()
    worker = setup_gaplic_thread(ga)
    worker.start()


.. autofunction:: setup_gaplic_thread

.. autoclass:: GAplicThreadWorker
    :members: run, join

Subprocess context
==================

Running as subprocess::

    ga = GAplic()
    worker = setup_gaplic_process(ga)
    worker.start()


.. autofunction:: setup_gaplic_process

.. autoclass:: GAplicProcessWorker
    :members: run, join


Runnig several threads or subprocesses::

    from ginsfsm.gaplic import GAplic, setup_gaplic_thread

    # run one gaplic as thread
    ga_srv = GAplic('Server')
    srv_worker = setup_gaplic_thread(ga_srv)
    srv_worker.start()

    ga_cli = GAplic('Client')

    try:
        # run the main gaplic as main process
        ga_cli.start()

    except (KeyboardInterrupt, SystemExit):
        # stop the main gaplic
        ga_srv.stop()

        # wait to finish the other gaplic
        srv_worker.join()

        print('Program stopped')



Ini file configuration
======================

You can configure and run your gaplic applications with PasteDeploy.

Available are the :term:`gcreate` and :term:`gserve` commands,
similar to pcreate and pserve of Pyramid.


.. autofunction:: gaplic_factory

"""
import time
import threading
from collections import deque

from ginsfsm.globals import (
    set_global_main_gaplic,
    set_global_app,
    add_global_thread,
    add_global_subprocess,
    get_gaplic_by_thread_ident,
)
from ginsfsm.compat import (
    string_types,
    iterkeys_,
)
from ginsfsm.deferred import (
    DeferredList,
    Deferred,
)
from ginsfsm.c_sock import (
    poll_loop,
    close_all_sockets,
    _poll,
    GSock,
)
from ginsfsm.gobj import GObj
from ginsfsm.router import GRouter


def _start_timer(seconds):
    """ Start a timer of :param:`seconds` seconds.
    The returned value must be used to check the end of the timer
    with _test_timer() function.
    """
    timer = time.time()
    timer = timer + seconds
    return timer


def _test_timer(value):
    """ Check if timer :param:`value` has ended.
    Return True if the timer has elapsed, False otherwise.
    WARNING: it will fail when system clock has been changed.
    TODO: check if system clock has been changed.
    """
    timer_actual = time.time()
    if timer_actual >= value:
        return True
    else:
        return False


class _XTimer(object):
    """  Group attributes for timing.
    :param:`got_timer` callback will be executed :param:`sec` seconds.
    The callback will be called with :param:`param1` parameter.
    If :param:`autostart` is True, the timer will be cyclic.
    """
    def __init__(self, sec, got_timer_func, param1, autostart):
        self.sec = sec
        self.got_timer_func = got_timer_func
        self.param1 = param1
        self.autostart = autostart


GAPLIC_FSM = {}

#def ac_deferred_callback(self, event):
#    deferred_ref = event.deferred_ref
#    self.deferred_list(deferred_ref, ext_event=event)
#    self.deferred_list.delete(deferred_ref)
#
#GAPLIC_FSM = {
#    'event_list': ('EV_DEFERRED_CALLBACK: top input',),
#    'state_list': ('ST_IDLE',),
#    'machine': {
#        'ST_IDLE':
#        (
#            ('EV_DEFERRED_CALLBACK', ac_deferred_callback, 'ST_IDLE'),
#        ),
#    }
#}

GAPLIC_GCONFIG = {
    'roles': [tuple, (), 0, None, 'Roles of gaplic'],
    'ini_settings': [
        dict, {}, 0, None,
        'The ini settings will be set to all new created gobj'
        ' by overwrite_parameters() function'
    ],
    # trace_mach is inherited from SMachine.
    'trace_mach': [bool, False, 0, None, 'Display simple machine activity'],
    # logger is inherited from SMachine.
    'logger': [None, None, 0, None, ''],
    'router_enabled': [
        bool, False, 0, None,
        'True if a (NOT Pyramid) router is enabled.'
    ],
    'all_unique_names': [
        bool, False, 0, None,
        'All named-gobjs are unique-named gobjs'
    ],
}


class GAplic(GObj):
    """ Container of gobj's running under the same process or thread.

    :param name: name of the gaplic, default is ``None``.
    :param ini_settings: keyword arguments,
        with the parameters from a ini configfile.
        The ini settings will be set to all new created gobj
        by :func:`ginsfsm.gobj.GObj.overwrite_parameters` function.


        .. note::

           The parameters can be dot named to include
           the :term:`named-gobj`'s destination of the parameters.


    GAplic is the main boss.
    Manage the timer's, event queues, etc.
    Supplies register, deregister and search or named-events.

    .. ginsfsm::
       :fsm: GAPLIC_FSM
       :gconfig: GAPLIC_GCONFIG

    Example::

        from ginsfsm.gaplic import GAplic

        if __name__ == "__main__":
            ga = GAplic(name='Example1')
            ga.create_gobj('test_aplic', GPrincipal, None)
            try:
                ga.start()
            except KeyboardInterrupt:
                print('Program stopped')

    """
    def __init__(self, name=None, roles=None, **ini_settings):
        GObj.__init__(self, GAPLIC_FSM, GAPLIC_GCONFIG)
        self.name = name
        # TODO: register in gaplic-dns: (gaplic_name, roles, urls)
        if isinstance(roles, (list, tuple)):
            self.roles = roles
        else:
            self.roles = (roles,)
        self.ini_settings = ini_settings.copy()
        # Call stop() to stop gaplic
        self.do_exit = multiprocessing.Event()
        """ threading.Event() or multiprocessing.Event() object
        to signal the stop of gaplic."""
        self.loop_timeout = 0.5     # timeout to select(),poll() function.
        """ Loop timeout. Default 0.5 seconds.
            It's the minimun timer resolution you can have.
        """
        self._impl_poll = _poll()   # Used by gsock. epoll() implementation.
        self._socket_map = {}       # Used by gsock. Dict {fd:Gobj}
        self._gotter_timers = {}    # Dict with timers  {_XTimer:timer value}
        self._qevent = deque()      # queue for post events.
        self._callbacks = []        # callbacks compatible with tornado.io_loop
        self._inside = 0            # to tab machine trace.
        self._unique_named_gobjs = {}
        self._thread_ident = None
        self._thread_name = 0
        self.gaplic = self
        self.deferred_list = DeferredList()

        logger = ini_settings.get('logger', None)
        if not logger:
            import logging
            self.logger = logging.getLogger(__name__)
        else:
            if isinstance(logger, string_types):
                import logging
                self.logger = logging.getLogger(logger)
            else:
                self.logger = logger
        if not self.logger:
            logging.basicConfig(level=logging.DEBUG)
            self.logger = logging

        self.start_up()

    def start_up(self):
        """ Initialization zone.
        """
        self.router_enabled = self.ini_settings.pop('router_enabled', False)
        self.all_unique_names = self.ini_settings.pop('all_unique_names',
                                                      False)

        if self.router_enabled:
            self.start_up_router()
        self.logger and self.logger.info('GAplic (%r) initiated' % self.name)

    def start_up_router(self, pyramid_url=None, pyramid_root=None):
        self.router = self.create_gobj(
            'router',
            GRouter,
            self,
            __unique_name__=True,
            pyramid_root=pyramid_root,
            pyramid_url=pyramid_url
        )

    def _increase_inside(self):
        self._inside += 1

    def _decrease_inside(self):
        self._inside -= 1

    def _tab(self):
        if self._inside <= 0:
            spaces = 1
        else:
            spaces = self._inside * 2
        pad = ' ' * spaces
        return pad

    def create_gobj(self, name, gclass, parent, **kw):
        """ Factory function to create gobj's instances.

        Subclass of :meth:`ginsfsm.gobj.GObj.create_gobj` to do something else,
        like to let :term:`unique-named-gobj` instances.

        :param name: Name of the gobj.
            If the key `__unique_name__` passed in *kw* is True,
            then the gobj will be a :term:`unique-named-gobj` and.
            the :meth:`GObj._register_unique_gobj` will be called.
            If :meth:`GObj._register_unique_gobj` fails, a
            :exc:GObjError exception will be raised.

        :param gclass: `gclass` is the GObj type used to create the new gobj.
            It's must be a derived class of :class:`ginsfsm.gobj.GObj`.

        :param parent: parent of the new :term:`gobj`.
            If `None`, the gobj will be a :term:`principal` gobj.

        :param kw: Attributes that are added to the new :term:`gobj`.
            All the keyword arguments used in the creation function
            **are added as attributes** to ``config`` object.

            You must consult the attributes supported
            by each `gclass` type.
            The attributes must be defined in the gclass GCONFIG,
            otherwise they are ignored.

            Special kw:

                ``'__unique_name__'``: Register the gobj as unique name gobj.

        :rtype: new gobj instance.

        When a :term:`gobj` is created by the factory function, it's added to
        their parent child list :attr:`ginsfsm.gobj.GObj.dl_childs`,
        and several attributes are created:

        * **parent**: the parent :term:`gobj` of the created :term:`gobj`.
        * **gaplic**: the :term:`gaplic` of the created :term:`gobj`.

        If the `gclass` is subclass of :class:`ginsfsm.c_sock.GSock`
        two private attributes are added to the created  :term:`gobj`:

        * **_socket_map**: dictionary of open sockets.
        * **_impl_poll**: poll implementation: can be epoll, select, KQueue..
          the best found option.

        It's the base of the asynchronous behavior.
        """
        attrs = {
            'logger': self.logger,
            'gaplic': self,
            'create_gobj': self.create_gobj,
            'destroy_gobj': self.destroy_gobj,
            '_increase_inside': self._increase_inside,
            '_decrease_inside': self._decrease_inside,
            '_tab': self._tab,
        }
        if issubclass(gclass, GSock):
            attrs.update({
                '_socket_map': self._socket_map,
                '_impl_poll': self._impl_poll
            })

        if self.all_unique_names:
            attrs.update({'__unique_name__': True})

        kw.update(attrs)

        gobj = GObj.create_gobj(self, name, gclass, parent, **kw)

        return gobj

    @staticmethod
    def destroy_gobj(gobj):
        """ Destroy a gobj
        """
        if gobj.__unique_name__:
            gobj.gaplic._deregister_unique_gobj(gobj)
        GObj.destroy_gobj(gobj)

    def get_unique_named_gobjs(self):
        """ Return the list of :term:`unique-named-gobj`'s.
        """
        return [name for name in iterkeys_(self._unique_named_gobjs)]

    def _register_unique_gobj(self, gobj):
        """ Register a :term:`unique-named-gobj`.
        """
        named_gobj = self._unique_named_gobjs.get(gobj.name, None)
        if named_gobj is not None:
            self.logger and self.logger.info(
                'ERROR _register_unique_gobj() "%s" ALREADY REGISTERED' %
                gobj.name)
            return False
        self._unique_named_gobjs[gobj.name] = gobj
        self.__unique_name__ = True
        return True

    def _deregister_unique_gobj(self, gobj):
        """ Deregister a :term:`unique-named-gobj`.
        """
        named_gobj = self._unique_named_gobjs.get(gobj.name, None)
        if named_gobj is not None:
            del self._unique_named_gobjs[gobj.name]
            return True
        return False

    def find_unique_gobj(self, gobj_name):
        """ Find a :term:`unique-named-gobj`.
        """
        named_gobj = self._unique_named_gobjs.get(gobj_name, None)
        return named_gobj

    def send_event_to_external_role(
            self, role, gobj_name, event_name, subscriber_gobj, **kw):
        """ Send an event to an external gaplic.

        :param role: name of external role.
        :param gobj_name: name of external gobj.
        :param event_name: name of the event to send.
        :param subscriber_gobj: subscriber obj that wants receive the response.
        :param kw: keyword arguments.

        Possible values for **kw** arguments:
            * `__subscribe_response__`: ``Bool`` Subscribe the
              response of external executed action.
              Received with the same event.
        """
        if not isinstance(role, string_types):
            raise TypeError(
                'Destination role %r must be a string'
                % (role)
            )
        if not isinstance(gobj_name, string_types):
            raise TypeError(
                'Destination gobj %r must be a string'
                % (gobj_name)
            )

        if not isinstance(event_name, string_types):
            raise TypeError(
                'Event name %r must be a string'
                % (event_name)
            )

        if not isinstance(subscriber_gobj, (string_types, GObj)):
            raise TypeError(
                'Subscriber gobj %r must be a string'
                % (subscriber_gobj)
            )

        if role in self.roles:
            raise TypeError(
                "Please don't use external methods to self gaplic."
                % (role)
            )

        if isinstance(subscriber_gobj, (GObj)):
            subscriber_gobj = subscriber_gobj.name

        subs_gobj = self.find_unique_gobj(subscriber_gobj)
        if not subs_gobj:
            raise TypeError(
                'Subscriber gobj %r must be a __unique_named__ gobj'
                % (subscriber_gobj)
            )

        return self.router.mt_send_event_to_external_role(
            role,
            gobj_name,
            event_name,
            subscriber_gobj,
            kw
        )

    def send_event_to_external_gaplic(
            self, gaplic_name, gobj_name, event_name, subscriber_gobj, **kw):
        """ Send an event to an external gaplic.

        :param gaplic_name: name of external gaplic.
        :param gobj_name: name of external gobj.
        :param event_name: name of the event to send.
        :param subscriber_gobj: subscriber obj that wants receive the response.
        :param kw: keyword arguments.

        Possible values for **kw** arguments:
            * `__subscribe_response__`: ``Bool`` Subscribe the
              response of external executed action.
              Received with the same event.
        """
        if not isinstance(gaplic_name, string_types):
            raise TypeError(
                'Destination gaplic %r must be a string'
                % (gaplic_name)
            )
        if not isinstance(gobj_name, string_types):
            raise TypeError(
                'Destination gobj %r must be a string'
                % (gobj_name)
            )

        if not isinstance(event_name, string_types):
            raise TypeError(
                'Event name %r must be a string'
                % (event_name)
            )

        if not isinstance(subscriber_gobj, (string_types, GObj)):
            raise TypeError(
                'Subscriber gobj %r must be a string'
                % (subscriber_gobj)
            )

        if gaplic_name == self.name:
            raise TypeError(
                "Please don't use external methods to self gaplic."
                % (gaplic_name)
            )

        if isinstance(subscriber_gobj, (GObj)):
            subscriber_gobj = subscriber_gobj.name

        subs_gobj = self.find_unique_gobj(subscriber_gobj)
        if not subs_gobj:
            raise TypeError(
                'Subscriber gobj %r must be a __unique_named__ gobj'
                % (subscriber_gobj)
            )

        return self.router.mt_send_event_to_external_gaplic(
            gaplic_name,
            gobj_name,
            event_name,
            subscriber_gobj,
            kw
        )

    def subscribe_event_from_external_gaplic(
            self, gaplic_name, gobj_name, event_name, subscriber_gobj, **kw):
        """ Subscribe an event of an external gaplic by name.
        """
        kw.update({'__subscribe_event__': True})
        return self.send_event_to_external_gaplic(
            gaplic_name,
            gobj_name,
            event_name,
            subscriber_gobj,
            **kw
        )

    def subscribe_event_from_external_role(
            self, role, gobj_name, event_name, subscriber_gobj, **kw):
        """ Subscribe an event of an external gaplic by role.
        """
        kw.update({'__subscribe_event__': True})
        return self.send_event_to_external_role(
            role,
            gobj_name,
            event_name,
            subscriber_gobj,
            **kw
        )

    def unsubscribe_event_from_external_gaplic(
            self, gaplic_name, gobj_name, event_name, subscriber_gobj, **kw):
        """ Subscribe an event of an external gaplic by name.
        """
        kw.update({'__unsubscribe_event__': True})
        return self.send_event_to_external_gaplic(
            gaplic_name,
            gobj_name,
            event_name,
            subscriber_gobj,
            **kw
        )

    def unsubscribe_event_from_external_role(
            self, role, gobj_name, event_name, subscriber_gobj, **kw):
        """ Subscribe an event of an external gaplic by role.
        """
        kw.update({'__unsubscribe_event__': True})
        return self.send_event_to_external_role(
            role,
            gobj_name,
            event_name,
            subscriber_gobj,
            **kw
        )

    def delete_all_references(self, gobj):
        """ Delete all references of gobj in timer and event queues.
        """
        # TODO: by the moment, be care with your event generation

    def _loop(self):
        """ process event queue, timer queue, and epoll.
        Return True if there is some remain event for be proccessed.
        Useful for testing purposes.
        """
        if not self._thread_ident:
            self._thread_ident = threading.current_thread().ident
            self._thread_name = threading.current_thread().name

        timeout = self.loop_timeout  # iniatially wait loop_timeout seconds
        remain = False  # some work pending.

        # Callbacks compatible with tornado.io_loop
        # Prevent IO event starvation by delaying new callbacks
        # to the next iteration of the event loop.
        callbacks = self._callbacks
        if callbacks:
            remain = True
            self._callbacks = []
            for callback in callbacks:
                self._run_callback(callback)

        if self._callbacks:
            # If any callbacks or timeouts called add_callback,
            # we don't want to wait in poll() before we run them.
            timeout = 0.0

        remain |= self._process_qevent()
        if remain:
            # They are remain events,
            # we don't want to wait in poll() before we run them.
            # wait some time, t
            # o avoid recursive send events that puts 100% cpu.
            # TODO: try set 0.0.
            timeout = 0.1

        poll_loop(self._socket_map, self._impl_poll, timeout)

        #
        remain |= self._process_timer()  # don't remove or the tests will fail.

        # oportunity for subclass.
        self.mt_subprocess()

        return remain

    def start(self):
        """ Run the infinite i/o event loop.
        """
        while True:
            # with do_exit Event set (being thread or process),
            # wait to event set to exit, ignoring KeyboardInterrupt.
            try:
                if self.do_exit.is_set():
                    close_all_sockets(self._socket_map)
                    break
                self._loop()
            except (KeyboardInterrupt, SystemExit):
                close_all_sockets(self._socket_map)
                raise

    def stop(self):
        """ Signalize the gaplic instance to stop.
        """
        self.do_exit.set()

    def mt_subprocess(self):
        """ Subclass :class:`GAplic` class and override this function
        to do extra work in the infinite loop.
        """

    def enqueue_event(self, event):
        """ Post the event in the next :term:`gaplic` loop cycle,
        not right now.

        :param event: :term:`event` to send.
        :param destination: destination :term:`gobj` of the event.
        :param kw: keyword argument with data associated to event.

            .. note::
                All the keyword arguments **are added as attributes** to
                the sent :term:`event`.

        Same as :meth:`send_event` function but the event is sent in the
        next :term:`gaplic` loop cycle, not right now.

        It **does not return** the return of the executed action because the
        action it's executed later, in the next loop cycle.

        It's mandatory use this function, if the `destination`
        :term:`gobj` is not local.

        .. note:: It **DOES NOT** return the return of the executed action
            because the action it's executed later, in the next loop cycle,
            so you **CANNOT** receive valid direct data from the action.

        .. warning:: If you use :meth:`post_event` without a :term:`gaplic`
            then a :exc:`GAplicError` exception will be raised.

        ``destination`` must be a `string` or :class:`GObj` types, otherwise a
        :exc:`GObjError` will be raised.

        ``event`` must be a `string` or :class:`Event` types, otherwise a
        :exc:`EventError` will be raised.

        If ``event`` is an :class:`Event` instance, a new :class:`Event`
        duplicated instance is returned, but it will be updated with
        the new ``destination`` and ``kw`` keyword arguments.

        .. note::
            All the keyword arguments used in the factory function
            **are added as attributes** to the created :term:`event` instance.
            You must consult the attributes supported by each machine's event.
        """
        self._qevent.append(event)

    def _process_qevent(self):
        """ Return True if remains events.
        """
        # ln = len(self._qevent)
        # print "qevent...........%d" % (ln)
        it = 0
        maximum = 10
        while True:
            if it > maximum:
                # balance the work
                return True
            try:
                event = self._qevent.popleft()
            except IndexError:
                break
            else:
                it += 1
                # To send to external gaplics, destination must be 'router'
                try:
                    destination = self._resolv_destination(event.destination)
                    cur_ident = threading.current_thread().ident
                    if cur_ident != self._thread_ident:
                        if self.logger:
                            self.logger.error("??????????????????")

                    dst_ident = destination.gaplic._thread_ident
                    if cur_ident == dst_ident:
                        self.send_event(
                            destination,
                            event.event_name,
                            **event.kw)
                    else:
                        # Yeah, send to another gaplic
                        gaplic = get_gaplic_by_thread_ident(dst_ident)
                        if gaplic:
                            gaplic.enqueue_event(event)
                except Exception:
                    if self.logger:
                        self.logger.error("Exception gaplic.__process_qevent")

        return False

    def _process_timer(self):
        # don't use iteritems() items(),
        # some xtimer can be removed during processing timers
        some_event = False
        try:
            for xtimer in iterkeys_(self._gotter_timers):
                try:
                    value = self._gotter_timers[xtimer]
                except KeyError:
                    # timer deleted while loop.
                    continue
                some_event = True
                if value and _test_timer(value):
                    if xtimer.autostart:
                        self._gotter_timers[xtimer] = _start_timer(xtimer.sec)
                    else:
                        self._gotter_timers[xtimer] = 0
                    if xtimer.param1 is None:
                        xtimer.got_timer_func()
                    else:
                        xtimer.got_timer_func(xtimer.param1)
                    if not xtimer.autostart:
                        self._gotter_timers.pop(xtimer)
        except RuntimeError:
            # timer deleted while loop.
            some_event = True
        return some_event

    def _setTimeout(self, sec, got_timer_func, param1=None, autostart=False):
        """ Set a callback to be executed in ``sec`` seconds.
        Function used by :class:`GTimer` gobj. Not for general use.
        Return an object to be used in :func:`clearTimeout`.
        """
        xtimer = _XTimer(sec, got_timer_func, param1, autostart)
        self._gotter_timers[xtimer] = _start_timer(sec)
        return xtimer

    def _clearTimeout(self, xtimer):
        """ Clear callback timeout.
        Function used by :class:`GTimer` gobj. Not for general use.
        """
        t = self._gotter_timers.get(xtimer, None)
        if t:
            # prevent timer cleared in proces_timer loop
            self._gotter_timers[xtimer] = 0
            self._gotter_timers.pop(xtimer)

    def add_timeout(self, deadline, callback):
        """ Compatible with tornado.io_loop

        ``deadline`` only seconds please.

        Calls the given callback at the time deadline from the I/O loop.

        Returns a handle that may be passed to remove_timeout to cancel.

        ``deadline`` may be a number denoting a unix timestamp (as returned
        by ``time.time()`` or a ``datetime.timedelta`` object for a deadline
        relative to the current time.

        Note that it is not safe to call `add_timeout` from other threads.
        Instead, you must use `add_callback` to transfer control to the
        IOLoop's thread, and then call `add_timeout` from there.
        """
        timer_id = self._setTimeout(deadline, callback)
        return timer_id

    def remove_timeout(self, timeout):
        """ Compatible with tornado.io_loop

        Cancels a pending timeout.

        The argument is a handle as returned by add_timeout.
        """
        # Removing from a heap is complicated, so just leave the defunct
        # timeout object in the queue (see discussion in
        # http://docs.python.org/library/heapq.html).
        # If this turns out to be a problem, we could add a garbage
        # collection pass whenever there are too many dead timeouts.
        timeout.callback = None
        self._clearTimeout(timeout)

    def add_callback(self, callback, *args, **kwargs):
        """ Call the given callback in the next I/O loop iteration.
        """
        list_empty = not self._callbacks
        deferred = Deferred(0, callback, *args, **kwargs)
        self._callbacks.append(deferred)
        if list_empty:
            if threading.current_thread().ident != self._thread_ident:
                # If we're in the IOLoop's thread, we know it's not currently
                # polling.  If we're not, and we added the first callback to an
                # empty list, we may need to wake it up (it may wake up on its
                # own, but an occasional extra wake is harmless).  Waking
                # up a polling IOLoop is relatively expensive, so we try to
                # avoid it when we can.
                pass
                # TODO: study this from tornado
                # self._waker.wake()

    def _run_callback(self, deferred):
        try:
            deferred()
        except Exception:
            self.handle_callback_exception(deferred)

    def handle_callback_exception(self, callback):
        """This method is called whenever a callback run by the IOLoop
        throws an exception.

        By default simply logs the exception as an error.  Subclasses
        may override this method to customize reporting of exceptions.

        The exception itself is not passed explicitly, but is available
        in sys.exc_info.
        """
        if self.logger:
            self.logger.error(
                "Exception in callback %r",
                callback,
                exc_info=True)


#===============================================================
#                   Thread wrapper for gaplic
#===============================================================
class GAplicThreadWorker(threading.Thread):
    """ Class derived from :class:`threading.Thread` to run gaplic
    in thread environment.
    """
    def __init__(self, gaplic):
        threading.Thread.__init__(self)
        self.daemon = True
        self.gaplic = gaplic

    def run(self):
        """ Override the :meth:`threading.Thread.run` method.

        Run the gaplic loop in a separate thread.
        """
        self.gaplic.start()

    def stop(self):
        """ Stop the worker.
        """
        self.gaplic.stop()

    def join(self, timeout=10.0):   # wait until 10 seconds for thread killed.
        """ Wait for worker to stop, until ``timeout`` seconds."""
        super(GAplicThreadWorker, self).join(timeout)


def setup_gaplic_thread(gaplic):
    """ Run gaplic as thread.
    Return the worker.
    You must call worker.start() to run the thread.
    """
    worker = GAplicThreadWorker(gaplic)
    add_global_thread(worker)
    return worker

#===============================================================
#                   Process wrapper for gaplic
#===============================================================
import multiprocessing


class GAplicProcessWorker(multiprocessing.Process):
    """ Class derived from :class:`multiprocessing.Process` to run gaplic
    in subprocess environment.
    """
    def __init__(self, gaplic):
        multiprocessing.Process.__init__(self)
        self.daemon = True
        self.gaplic = gaplic

    def run(self):
        """ Override the :meth:`multiprocessing.Process.run` method.

        Run the gaplic loop in a separate process.
        """
        self.gaplic.start()

    def stop(self):
        """ Stop the worker.
        """
        self.gaplic.stop()

    def join(self, timeout=10.0):   # wait until 10 seconds for process killed.
        """ Wait for worker to stop, until ``timeout`` seconds."""
        super(GAplicProcessWorker, self).join(timeout)


def setup_gaplic_process(gaplic):
    """ Run gaplic as process.
    Return the worker.
    You must call worker.start() to run the subprocess.
    """
    worker = GAplicProcessWorker(gaplic)
    add_global_subprocess(worker)
    return worker


def gaplic_factory(loader, global_conf, **local_conf):
    """ To use with PasteDeploy in composite.

        Items of *composite* section:

        :main: name of a section that must return a :term:`gaplic`
               instance. It will be the **principal** :term:`gaplic`.

        :threads: name of sections that must return :term:`gaplic`
               instances. They will run in threads.

        :subprocesses: name of sections that must return :term:`gaplic`
               instances. They will run in subprocesses.

        :wsgi: name of sections that must return a *app paste factory*.
            Wsgi applications are saved as global apps (set_global_app()).


        Example::

            [composite:main]
            use = call:ginsfsm.gaplic:gaplic_factory
            main = wsgi-server
            wsgi = wsgi-application

            [app:wsgi-server]
            use = call:ginsfsm.examples.wsgi.simple_wsgi_server:main
            host = 0.0.0.0
            port = 8000
            application = wsgi-application
            GSock.trace_dump = true
            GObj.trace_mach = true

            [app:wsgi-application]
            use=call:ginsfsm.examples.wsgi.simple_wsgi_server:paste_app_factory


    The prototype for ``wsgi`` (paste app factory) is::

        def paste_app_factory(global_conf, **local_conf):
            return wsgi-application

    The prototype for ``main``, ``threads`` and ``subprocesses`` is::

        def main(global_conf, **local_config):
            return gaplic-instance

    """
    main = local_conf.get('main')
    wsgis = local_conf.get('wsgi', '').split()
    threads = local_conf.get('threads', '').split()
    subprocesses = local_conf.get('subprocesses', '').split()

    # Firstly create main gaplic, to can pass it to wsgi's
    main_gaplic = loader.get_app(main, global_conf=global_conf)
    set_global_main_gaplic(main_gaplic)

    for thread in threads:
        gaplic = loader.get_app(thread, global_conf=global_conf)
        worker = setup_gaplic_thread(gaplic)
        worker.start()

    for subprocess in subprocesses:
        gaplic = loader.get_app(subprocess, global_conf=global_conf)
        worker = setup_gaplic_process(gaplic)
        worker.start()

    for wsgi in wsgis:
        app = loader.get_app(wsgi, global_conf=global_conf)
        set_global_app(wsgi, app)

    return main_gaplic
