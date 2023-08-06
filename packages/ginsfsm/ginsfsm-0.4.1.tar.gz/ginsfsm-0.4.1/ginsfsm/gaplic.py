# -*- encoding: utf-8 -*-
""" Container of gobjs.


.. autoclass:: GAplic
    :members: create_gobj, destroy_gobj,
        register_unique_gobj, deregister_unique_gobj, find_unique_gobj,
        mt_process, mt_subprocess

.. autofunction:: setup_gaplic_thread

.. autoclass:: GAplicThreadWorker
    :members:

.. autofunction:: setup_gaplic_process

.. autoclass:: GAplicProcessWorker
    :members:

.. autofunction:: gaplic_factory

"""
import time
import threading
import logging
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
)
from ginsfsm.c_sock import (
    poll_loop,
    close_all_sockets,
    _poll,
    GSock,
)
from ginsfsm.gobj import (
    GObj,
)


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


def ac_deferred_callback(self, event):
    deferred_ref = event.deferred_ref
    self.deferred_list(deferred_ref, ext_event=event)
    self.deferred_list.delete(deferred_ref)

GAPLIC_FSM = {
    'event_list': ('EV_DEFERRED_CALLBACK',),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_DEFERRED_CALLBACK', ac_deferred_callback, 'ST_IDLE'),
        ),
    }
}

GAPLIC_GCONFIG = {
    'ini_settings': [dict, {}, 0, None,
        'The ini settings will be set to all new created gobj'
        ' by overwrite_parameters() function'],
    # trace_mach is inherited from SMachine.
    'trace_mach': [bool, False, 0, None, 'Display simple machine activity'],
    # logger is inherited from SMachine.
    'logger': [None, None, 0, None, ''],
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

    Example::

        if __name__ == "__main__":
            ga = GAplic(name='Example1')
            ga.create_gobj('test_aplic', GPrincipal, None)
            try:
                ga.mt_process()
            except KeyboardInterrupt:
                print('Program stopped')

    """
    def __init__(self, name=None, **ini_settings):
        GObj.__init__(self, GAPLIC_FSM)
        self.name = name
        self.ini_settings = ini_settings.copy()
        # Call shutdown() to stop gaplic
        self.do_exit = multiprocessing.Event()
        """threading.Event() or multiprocessing.Event() object
        to signal the shutdown of gaplic."""
        self.loop_timeout = 0.5     # timeout to select(),poll() function.
        """Loop timeout. Default 0.5 seconds."""
        self._impl_poll = _poll()   # Used by gsock. epoll() implementation.
        self._socket_map = {}       # Used by gsock. Dict {fd:Gobj}
        self._gotter_timers = {}    # Dict with timers  {_XTimer:timer value}
        self._qevent = deque()      # queue for post events.
        self._inside = 0            # to tab machine trace.
        self._unique_named_gobjs = {}
        self.thread_ident = 0
        self.thread_name = 0
        self.gaplic = self
        self.deferred_list = DeferredList()

        logger = ini_settings.get('logger', None)
        if logger is None:
            # TODO use package caller
            self.logger = logging.getLogger(__name__)
        else:
            if isinstance(logger, string_types):
                self.logger = logging.getLogger(logger)
            else:
                self.logger = logger
        self.logger and self.logger.info('GAplic (%s) initiated' % self.name)

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

        :param name: Name of gobj.
            You can create :term:`named-gobj` or :term:`unnamed-gobj` gobjs.
            :term:`named-gobj` gobjs can be reached by his name,
            but the :term:`unnamed-gobj` gobjs
            are only knowing by their `pointer`.

        :param gclass: `gclass` is the GObj type used to create the new gobj.
            It's must be a derived class of :class:`ginsfsm.gobj.GObj`.
        :param parent: parent of the new :term:`gobj`.
            If `None`, the gobj will be a :term:`principal` gobj and
            their parent will be :term:`gaplic`.
        :param kw: Attributes that are added to the new :term:`gobj`.
            All the keyword arguments used in the function
            **are added as attributes** to the created :term:`gobj`.
            You must consult the attributes supported
            by each `gclass` type.
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
        if parent is None:
            parent = self

        _gaplic_kw = {
            'gaplic': self,
            'logger': self.logger,
            'ini_settings': self.ini_settings,
            'create_gobj': self.create_gobj,
            'enqueue_event': self.enqueue_event,
            'register_unique_gobj': self.register_unique_gobj,
            'deregister_unique_gobj': self.deregister_unique_gobj,
            'find_unique_gobj': self.find_unique_gobj,
            'delete_all_references': self.delete_all_references,
            '_increase_inside': self._increase_inside,
            '_decrease_inside': self._decrease_inside,
            '_tab': self._tab,
        }

        if issubclass(gclass, GSock):
            _gaplic_kw.update({
                '_socket_map': self._socket_map,
                '_impl_poll': self._impl_poll
            })

        kw.update(_gaplic_kw)

        gobj = GObj.create_gobj(self, name, gclass, parent, **kw)
        return gobj

    def get_named_gobjs(self):
        """ Return the list of :term:`named-gobj`'s.
        """
        return [name for name in iterkeys_(self._unique_named_gobjs)]

    def register_unique_gobj(self, gobj):
        """ Register a :term:`named-gobj`.
        """
        named_gobj = self._unique_named_gobjs.get(gobj.name, None)
        if named_gobj is not None:
            self.logger and self.logger.info(
                'ERROR register_unique_gobj() "%s" ALREADY REGISTERED' %
                gobj.name)
            return False
        self._unique_named_gobjs[gobj.name] = gobj
        return True

    def deregister_unique_gobj(self, gobj):
        """ Deregister a :term:`named-gobj`.
        """
        named_gobj = self._unique_named_gobjs.get(gobj.name, None)
        if named_gobj is not None:
            del self._unique_named_gobjs[gobj.name]
            return True
        return False

    def find_unique_gobj(self, gobj_name):
        """ Find a :term:`named-gobj`.
        """
        named_gobj = self._unique_named_gobjs.get(gobj_name, None)
        return named_gobj

    def delete_all_references(self, gobj):
        """ Delete all references of gobj in timer and event queues.
        """
        # TODO: by the moment, be care with your event generation

    def _loop(self):
        """ process event queue, timer queue, and epoll.
        Return True if there is some remain event for be proccessed.
        Useful for testing purposes.
        """
        if not self.thread_ident:
            self.thread_ident = threading.current_thread().ident
            self.thread_name = threading.current_thread().name
        remain = self._process_qevent()
        if remain:
            timeout = 0.01
        else:
            timeout = self.loop_timeout
        some_event = poll_loop(self._socket_map, self._impl_poll, timeout)
        if some_event:
            remain = True
        remain |= self._process_timer()

        self.mt_subprocess()
        return remain

    def mt_process(self):
        self.start()

    def start(self):
        """ Infinite loop function to be called by thread or process.
        It's call ``start`` to be used by pasterdeploy
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

    def shutdown(self):
        """ Signalize the worker to shutdown """
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
                #TODO consider names of another gaplics
                destination = self._resolv_destination(event.destination)
                cur_ident = threading.current_thread().ident
                dst_ident = destination.gaplic.thread_ident
                if cur_ident == dst_ident:
                    self.send_event(destination, event.event_name, **event.kw)
                else:
                    # Yeah, send to another gaplic
                    gaplic = get_gaplic_by_thread_ident(dst_ident)
                    if gaplic:
                        gaplic.enqueue_event(event)
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


#===============================================================
#                   Thread wrapper for gaplic
#===============================================================
class GAplicThreadWorker(threading.Thread):
    """ Class derived from :class:`threading.Thread` to run gaplic."""
    def __init__(self, gaplic):
        threading.Thread.__init__(self)
        self.daemon = True
        self.gaplic = gaplic

    def run(self):
        self.gaplic.mt_process()

    def join(self, timeout=10.0):   # wait until 10 seconds for thread killed.
        """ Wait for worker to shutdown, until ``timeout`` seconds."""
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
    """ Class derived from :class:`multiprocessing.Process` to run gaplic."""
    def __init__(self, gaplic):
        multiprocessing.Process.__init__(self)
        self.daemon = True
        self.gaplic = gaplic

    def run(self):
        self.gaplic.mt_process()

    def join(self, timeout=10.0):   # wait until 10 seconds for process killed.
        """ Wait for worker to shutdown, until ``timeout`` seconds."""
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

    for wsgi in wsgis:
        app = loader.get_app(wsgi, global_conf=global_conf)
        set_global_app(wsgi, app)

    gaplic_main = loader.get_app(main, global_conf=global_conf)
    set_global_main_gaplic(gaplic_main)

    for thread in threads:
        gaplic = loader.get_app(thread, global_conf=global_conf)
        worker = GAplicThreadWorker(gaplic)
        worker.start()

    for subprocess in subprocesses:
        gaplic = loader.get_app(subprocess, global_conf=global_conf)
        worker = GAplicProcessWorker(gaplic)
        worker.start()

    return gaplic_main
