import logging
import unittest

from mushroom.utils import Observable
from mushroom.utils import Signal


class NS(object):
    pass


class ObservableTestCase(unittest.TestCase):

    def test_set_and_get(self):
        o = Observable()
        value = object()
        self.assertIs(o(), None)
        o(value)
        self.assertIs(o(), value)

    def test_subscribe(self):
        o = Observable()
        ns = NS()
        ns.success = False
        ns.value = None
        def cb(value):
            ns.success = True
            ns.value = value
        o.subscribe(cb)
        value = object()
        self.assertIs(o(), None)
        o(value)
        self.assertTrue(ns.success)
        self.assertIs(ns.value, value)
        self.assertIs(o(), value)


class SignalTestCase(unittest.TestCase):

    def test_connect(self):
        s = Signal()
        ns = NS()
        ns.success = False
        ns.value = None
        def cb(value):
            ns.success = True
            ns.value = value
        s.connect(cb)
        value = object()
        s.send(value)
        self.assertTrue(ns.success)
        self.assertIs(ns.value, value)

    def test_disconnect(self):
        s = Signal()
        ns = NS()
        ns.success = False
        ns.value = None
        def cb(value):
            ns.success = True
            ns.value = value
        s.connect(cb)
        s.disconnect(cb)
        value = object()
        s.send(value)
        self.assertFalse(ns.success)
        self.assertIs(ns.value, None)
