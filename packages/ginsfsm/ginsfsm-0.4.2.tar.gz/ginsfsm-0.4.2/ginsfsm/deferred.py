# -*- coding: utf-8 -*-
import logging
from collections import (
    Callable,
    deque,
    )


class DeferredInterrupt(Exception):
    def __init__(self, deferred_ref):
        Exception.__init__(self)
        self.deferred_ref = deferred_ref


class Deferred(object):
    def __init__(self, ref, func, *args, **kwargs):
        """Return a new Deferred instance
        :param ref: Find a callback function by his reference.
        :param func: Deferred callback function.
        :param args: args to callback function.
        :param kwargs: kwargs to callback function.
        """
        assert isinstance(func, Callable)
        self.ref = ref
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}

    def __call__(self, **kwargs):
        """Processing the callback .
        """
        kw = self.kwargs.copy()
        kw.update(kwargs)
        return self.func(*self.args, **kw)


class DeferredList(object):
    """ List of deferred callbacks
        Add a callable (function or method).
    """
    def __init__(self):
        self.callbacks = deque()

    def add_callback(self, ref, func, *args, **kwargs):
        new_deferred = Deferred(ref, func, *args, **kwargs)
        self.callbacks.append(new_deferred)
        return new_deferred

    def __call__(self, ref, **kwargs):
        for deferred in self.callbacks:
            if deferred.ref == ref:
                return deferred(**kwargs)
        logging.error("ERROR __call__ deferred ref %r NOT FOUND" % deferred.ref)

    def delete(self, ref):
        for deferred in self.callbacks:
            if deferred.ref == ref:
                self.callbacks.remove(deferred)
                return
        logging.error("ERROR delete deferred ref %r NOT FOUND" % deferred.ref)
