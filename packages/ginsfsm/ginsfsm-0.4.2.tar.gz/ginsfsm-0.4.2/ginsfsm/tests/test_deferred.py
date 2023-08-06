import unittest
from ginsfsm.deferred import (
    Deferred,
    DeferredList,
    )


def func1(arg1, kwarg1=None):
    return (arg1, kwarg1)


def func2(*args, **kwargs):
    return (args, kwargs)


def func3(dst, event):
    def _func3(dst=dst, event=event):
        return (dst, event)
    return _func3


class TestDeferred(unittest.TestCase):
    def setUp(self):
        self.deferred_list = DeferredList()

    def test_callback1(self):
        self.deferred_list.add_callback(func1, func1, 1, kwarg1=2)
        result = self.deferred_list(func1)
        x, y = result
        self.assertEqual(x, 1)
        self.assertEqual(y, 2)

    def test_callback2(self):
        self.deferred_list.add_callback("refXXX", func2, 2, kwarg1=1, kwarg2=2)
        result = self.deferred_list("refXXX", kwarg3=3)
        l, d = result
        self.assertEqual(l[0], 2)
        self.assertEqual(d['kwarg1'], 1)
        self.assertEqual(d['kwarg2'], 2)
        self.assertEqual(d['kwarg3'], 3)

    def test_callback3(self):
        self.deferred_list.add_callback(None, func2, 2, kwarg1=1, kwarg2=2)
        result = self.deferred_list(None, kwarg3=3)
        l, d = result
        self.assertEqual(l[0], 2)
        self.assertEqual(d['kwarg1'], 1)
        self.assertEqual(d['kwarg2'], 2)
        self.assertEqual(d['kwarg3'], 3)

    def test_callback4(self):
        self.deferred_list.add_callback('XXX',
                                        func3(dst='gobj1', event='ev_event1'))
        result = self.deferred_list('XXX')
        d, e = result
        self.assertEqual(d, 'gobj1')
        self.assertEqual(e, 'ev_event1')

        result = self.deferred_list('XXX', dst='gobj2')
        d, e = result
        self.assertEqual(d, 'gobj2')
        self.assertEqual(e, 'ev_event1')
