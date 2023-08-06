# -*- coding: utf-8 -*-
from collections import (
    Callable,
    deque,
)


class DeferredInterrupt(Exception):
    def __init__(self, deferred_ref):
        Exception.__init__(self)
        self.deferred_ref = deferred_ref


class Deferred(object):
    def __init__(self, ref, callback, *args, **kwargs):
        """Return a new Deferred instance
        :param ref: Find a callback function by his reference.
        :param callback: Deferred callback function.
        :param args: args to callback function.
        :param kwargs: kwargs to callback function.
        """
        assert isinstance(callback, Callable)
        self.ref = ref
        self.callback = callback
        self.args = args or []
        self.kwargs = kwargs or {}
        self.cancelled = False

    def __call__(self, **kwargs):
        """Processing the callback .
        """
        if self.cancelled:
            return
        kw = self.kwargs.copy()
        kw.update(kwargs)
        return self.callback(*self.args, **kw)

    def cancel(self):
        """ Attempt to cancel the callback.
        """
        self.cancelled = True


class DeferredList(object):
    """ List of deferred callbacks
        Add a callable (function or method).
        The deferred callable are executed by searching his reference.
    """
    def __init__(self):
        self.callbacks = deque()

    def add_callback(self, ref, callback, *args, **kwargs):
        new_deferred = Deferred(ref, callback, *args, **kwargs)
        self.callbacks.append(new_deferred)
        return new_deferred

    def __call__(self, ref, **kwargs):
        for deferred in self.callbacks:
            if deferred.ref == ref:
                return deferred(**kwargs)
        print("ERROR __call__ deferred ref %r NOT FOUND" % (
            deferred.ref))

    def delete(self, ref):
        for deferred in self.callbacks:
            if deferred.ref == ref:
                self.callbacks.remove(deferred)
                return
        print("ERROR delete deferred ref %r NOT FOUND" % deferred.ref)
