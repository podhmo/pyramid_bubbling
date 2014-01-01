# -*- coding:utf-8 -*-
import unittest
from pyramid import testing
from testfixtures import compare

class A:
    pass
class B:
    def __init__(self, a):
        self.a = a
class C:
    def __init__(self, b):
        self.b = b


from zope.interface import (
    Interface,
    implementer
)
class INode(Interface):
    pass

@implementer(INode)
class X(object):
    pass

@implementer(INode)
class Y(object):
    parent = X
    def __init__(self, parent):
        self.parent = parent

@implementer(INode)
class Z(object):
    parent = Y
    def __init__(self, parent):
        self.parent = parent


class I(object):
    parent = None
    def on_called(self, subject):
        pass

class J(object):
    parent = I
    def __init__(self, parent):
        self.parent = parent
    def on_called(self, subject):
        pass

class K(object):
    parent = J
    def __init__(self, parent):
        self.parent = parent
    def on_called(self, subject):
        pass

class ConfigurationTestsBase(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include("pyramid_bubbling")

    def tearDown(self):
        testing.tearDown()
        from pyramid_bubbling.util import clean_dynamic_interface
        clean_dynamic_interface()

class ConfigurationVerifyBubblingPathTests(ConfigurationTestsBase):
    def test_each_path(self):
        from pyramid_bubbling.components import ParentFromInstance
        config = self.config

        config.add_bubbling_path(C, ParentFromInstance(lambda s:s.b, lambda c: B))
        config.add_bubbling_path(B, ParentFromInstance(lambda s:s.a, lambda c: A))

        config.verify_bubbling_path(C, [C, B, A])

    def test_each_path__missing1(self):
        from pyramid_bubbling.components import ParentFromInstance
        from pyramid_bubbling import BubblingConfigurationError
        config = self.config
        ##config.add_bubbling_path(C, ParentFromInstance(lambda s:s.b, lambda c: B))

        config.add_bubbling_path(B, ParentFromInstance(lambda s:s.a, lambda c: A))
        with self.assertRaises(BubblingConfigurationError):
            config.verify_bubbling_path(C, [C, B, A])

    def test_each_path__missing2(self):
        from pyramid_bubbling.components import ParentFromInstance
        from pyramid_bubbling import BubblingConfigurationError
        config = self.config

        config.add_bubbling_path(C, ParentFromInstance(lambda s:s.b, lambda c: B))
        ##config.add_bubbling_path(B, ParentFromInstance(lambda s:s.a, lambda c: A))

        with self.assertRaises(BubblingConfigurationError):
            config.verify_bubbling_path(C, [C, B, A])

    def test_simple(self):
        from pyramid_bubbling.components import ParentFromInstance
        config = self.config
        def access(s):
            return getattr(s, "parent", None)

        config.add_bubbling_path(INode, ParentFromInstance(access, access))
        config.verify_bubbling_path(Z, [Z, Y, X])


class ConfigurationBubblingVerifyEventTests(ConfigurationTestsBase):
    def test_not_bound__raise_expception(self):
        from pyramid_bubbling.components import ParentFromInstance
        from pyramid_bubbling import BubblingConfigurationError
        config = self.config

        config.add_bubbling_path(C, ParentFromInstance(lambda s:s.b, lambda c: B))
        config.add_bubbling_path(B, ParentFromInstance(lambda s:s.a, lambda c: A))

        with self.assertRaises(BubblingConfigurationError):
            result = config.verify_bubbling_event(C)
            compare(result, [None, None, None])


    def test_each_path(self):
        from pyramid_bubbling.components import ParentFromInstance
        config = self.config

        config.add_bubbling_path(C, ParentFromInstance(lambda s:s.b, lambda c: B))
        config.add_bubbling_path(B, ParentFromInstance(lambda s:s.a, lambda c: A))

        def called(subject):
            pass

        config.add_bubbling_event(C, called)
        config.add_bubbling_event(B, called)
        config.add_bubbling_event(A, called)

        result = config.verify_bubbling_event(C)
        compare(result, [called, called, called])


    def test_each_path__named(self):
        from pyramid_bubbling.components import ParentFromInstance
        config = self.config

        config.add_bubbling_path(C, ParentFromInstance(lambda s:s.b, lambda c: B))
        config.add_bubbling_path(B, ParentFromInstance(lambda s:s.a, lambda c: A))

        def called(subject):
            pass

        config.add_bubbling_event(C, called, "called")
        config.add_bubbling_event(B, called, "called")
        config.add_bubbling_event(A, called, "called")

        result = config.verify_bubbling_event(C, "called")
        compare(result, [called, called, called])


class ConfigurationForSimpleBubblingTests(ConfigurationTestsBase):
    def test_bubbling_path(self):
        from pyramid_bubbling import Accessor
        config = self.config
        config.verify_bubbling_path(K, [K, J, I], access=Accessor("parent"))

    def test__bubbling_path_lookup_failure(self):
        from pyramid_bubbling import BubblingConfigurationError
        from pyramid_bubbling import Accessor
        config = self.config
        with self.assertRaises(BubblingConfigurationError):
            config.verify_bubbling_path(K, [K, J, I], access=Accessor("*dummy*"))

    def test_bound_event(self):
        from pyramid_bubbling import Accessor
        config = self.config
        config.verify_bubbling_event(K, event_name="called", access=Accessor("parent"))

    def test_bound_event__another_event_name(self):
        from pyramid_bubbling import BubblingConfigurationError
        from pyramid_bubbling import Accessor
        config = self.config
        with self.assertRaises(BubblingConfigurationError):
            config.verify_bubbling_event(K, event_name="foo", access=Accessor("parent"))

if __name__ == '__main__':
    unittest.main()

