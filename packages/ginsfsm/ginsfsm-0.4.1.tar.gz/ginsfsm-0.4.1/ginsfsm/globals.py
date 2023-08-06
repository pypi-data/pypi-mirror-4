""" In the process domain there is no a only king.
There are applications (_global_apps),
there are threads (_global_threads),
and there are subprocesses (_global_subprocesses).

For now, the applications are only wsgi applications
to be used with wsgi-servers. Enough!!

Threads and subprocesses have their own king: his :term:`gaplic`.

And me, the main king, the main process of course.

"""
import atexit
import threading
import logging

_global_apps = {}
""" _global_apps is a dictionary with the wsgi applications
that are loaded from gaplic_factory when ini config file are processed.

They are defined in the ini config file, in ``others`` item:

        [composite:main]
        others = wsgi-application

        [app:wsgi-application]
        use = call:ginsfsm.examples.example6-wsgi-server:paste_app_factory

"""


def get_global_app(app_name):
    global _global_apps
    return _global_apps.get(app_name, None)


def set_global_app(app_name, callable):
    global _global_apps
    _global_apps[app_name] = callable


from collections import deque

_global_main = None
_global_threads = deque()
_global_subprocesses = deque()


def set_global_main_gaplic(gaplic):
    global _global_main
    _global_main = gaplic


def get_global_main_gaplic():
    global _global_main
    return _global_main


def add_global_thread(worker):
    global _global_threads
    _global_threads.append(worker)


def get_global_threads():
    global _global_threads
    return _global_threads


def add_global_subprocess(worker):
    global _global_subprocesses
    _global_subprocesses.append(worker)


def get_global_subprocesses():
    global _global_subprocesses
    return _global_subprocesses


@atexit.register
def shutdown():
    """ Stop all gaplic, main, threads and subprocesses.
    """
    timeout = 5  # enough seconds?

    global_threads = get_global_threads()
    while 1:
        try:
            wkr = global_threads.pop()
        except IndexError:
            break
        wkr.gaplic.shutdown()
        wkr.join(timeout)

    global_subprocesses = get_global_subprocesses()
    while 1:
        try:
            wkr = global_subprocesses.pop()
        except IndexError:
            break
        wkr.gaplic.shutdown()
        wkr.join(timeout)

    global_main = get_global_main_gaplic()
    if global_main:
        global_main.shutdown()


def global_get_gobj(gobj_name):
    """ Search a :term:`named-gobj` in global_main, threads and subprocesses.
    TODO: with subprocesses send_event() will work??
    """
    global_main_gaplic = get_global_main_gaplic()
    gobj = global_main_gaplic.find_unique_gobj(gobj_name)
    if gobj:
        return gobj

    global_threads = get_global_threads()
    for wkr in global_threads:
        gobj = wkr.gaplic.find_unique_gobj(gobj_name)
        if gobj:
            return gobj

    # TODO: will work???
    global_subprocesses = get_global_subprocesses()
    for wkr in global_subprocesses:
        gobj = wkr.gaplic.find_unique_gobj(gobj_name)
        if gobj:
            return gobj
    return None


def get_gaplic_by_thread_ident(thread_ident=None):
    """ Return the gaplic by the thread ident.
        If :param:`thread_ident` is None,
        then search by the caller thread ident.
    """
    if thread_ident is None:
        thread_ident = threading.current_thread().ident
    global_main_gaplic = get_global_main_gaplic()
    if global_main_gaplic is None:
        logging.error(
            "ERROR global main gaplic is NOT SET. "
            "Have you called set_global_main_gaplic()?."
        )
        raise Exception('ERROR global main gaplic not set.')
    if global_main_gaplic.thread_ident == thread_ident:
        return global_main_gaplic

    global_threads = get_global_threads()
    for wkr in global_threads:
        if wkr.gaplic.thread_ident == thread_ident:
            return wkr.gaplic

    # TODO: will work???
    global_subprocesses = get_global_subprocesses()
    for wkr in global_subprocesses:
        if wkr.gaplic.thread_ident == thread_ident:
            return wkr.gaplic
    return None
