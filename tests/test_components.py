# -*- coding:utf-8 -*-
import unittest
from testfixtures import compare
from zope.interface import Interface, implementer

class INode(Interface):
    pass

@implementer(INode)
class base(object):
    pass

def NodeFactory(name, iface_name, base=base):
    from zope.interface.interface import InterfaceClass
    def __init__(self, parent=None):
        self.parent = parent
    attrs = {"__init__": __init__}
    cls = type(name, (base, ), attrs)
    return implementer(InterfaceClass(iface_name))(cls)

def get_registry():
    from zope.interface.registry import Components
    return Components()

class BubblinglookupTests(unittest.TestCase):
    def _add_bubbling_path(self, *args, **kwargs):
        from pyramid_bubbling.components import _add_bubbling_path
        return _add_bubbling_path(*args, **kwargs)

    def _callFUT(self, *args, **kwargs):
        from pyramid_bubbling.components import _lookup
        return _lookup(*args, **kwargs)

    def test_it(self):
        from zope.interface import providedBy
        from pyramid_bubbling.components import ParentFromInstance
        A = NodeFactory("A", "IA")

        registry = get_registry()
        fn = ParentFromInstance(None, None)
        self._add_bubbling_path(registry, A, fn)
        result = self._callFUT(registry, [providedBy(A())])
        compare(result, fn)

class BubblingOrderTests(unittest.TestCase):
    def _add_bubbling_path(self, *args, **kwargs):
        from pyramid_bubbling.components import _add_bubbling_path
        return _add_bubbling_path(*args, **kwargs)

    def _getTargetClass(self):
        from pyramid_bubbling import Bubbling
        return Bubbling

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_setting_each_adapter(self):
        from pyramid_bubbling.components import ParentFromInstance
        ## c -> b -> a
        A = NodeFactory("A", "IA")
        B = NodeFactory("B", "IB")
        C = NodeFactory("C", "IC")

        registry = get_registry()
        self._add_bubbling_path(registry, A, ParentFromInstance(None, lambda cls: None));
        self._add_bubbling_path(registry, B, ParentFromInstance(None, lambda cls: A))
        self._add_bubbling_path(registry, C, ParentFromInstance(None, lambda cls: B))

        from pyramid_bubbling.components import RegistryAccessForClass
        target = self._makeOne(RegistryAccessForClass(registry))
        result = target.get_bubbling_path_order(C)
        compare(result, [C, B, A])

    def test_setting_default_one(self):
        from pyramid_bubbling.components import ParentFromInstance
        ## c -> b -> a
        A = NodeFactory("A", "IA")
        A.parent = None
        B = NodeFactory("B", "IB")
        B.parent = A
        C = NodeFactory("C", "IC")
        C.parent = B

        registry = get_registry()
        self._add_bubbling_path(registry, INode, ParentFromInstance(None, lambda cls: cls.parent));

        from pyramid_bubbling.components import RegistryAccessForClass
        target = self._makeOne(RegistryAccessForClass(registry))
        result = target.get_bubbling_path_order(C)
        compare(result, [C, B, A])

class BubblingEventRegistryTests(unittest.TestCase):
    def _add_bubbling_path(self, *args, **kwargs):
        from pyramid_bubbling.components import _add_bubbling_path
        return _add_bubbling_path(*args, **kwargs)

    def _add_bubbling_event(self, *args, **kwargs):
        from pyramid_bubbling.components import _add_bubbling_event
        return _add_bubbling_event(*args, **kwargs)

    def _getTargetClass(self):
        from pyramid_bubbling import Bubbling
        return Bubbling

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_it(self):
        from pyramid_bubbling.components import ParentFromInstance
        ## d -> c -> b -> a
        A = NodeFactory("A", "IA")
        B = NodeFactory("B", "IB")
        C = NodeFactory("C", "IC")
        D = NodeFactory("D", "ID")

        called = []
        def on_called(self):
            called.append(self)

        registry = get_registry()
        def lookup_parent(self):
            return self.parent
        self._add_bubbling_path(registry, A, ParentFromInstance(lookup_parent, None))
        self._add_bubbling_path(registry, B, ParentFromInstance(lookup_parent, None))
        self._add_bubbling_path(registry, C, ParentFromInstance(lookup_parent, None))
        self._add_bubbling_path(registry, D, ParentFromInstance(lookup_parent, None))

        self._add_bubbling_event(registry, A, on_called, name="called")
        self._add_bubbling_event(registry, B, on_called, name="called")
        self._add_bubbling_event(registry, C, on_called, name="called")
        self._add_bubbling_event(registry, D, on_called, name="called")

        a = A()
        b = B(a)
        c = C(b)
        d = D(c)

        from pyramid_bubbling.components import RegistryAccess
        target = self._makeOne(RegistryAccess(registry))
        target.fire(d, "called")
        compare(called, [d, c, b, a])

    def test_it__same_lookup(self):
        from pyramid_bubbling.components import ParentFromInstance
        ## d -> c -> b -> a
        A = NodeFactory("A", "IA")
        B = NodeFactory("B", "IB")
        C = NodeFactory("C", "IC")
        D = NodeFactory("D", "ID")


        called = []
        def on_called(self):
            called.append(self)

        registry = get_registry()
        def lookup_parent(self):
            return self.parent
        relation = ParentFromInstance(lookup_parent, None)
        self._add_bubbling_path(registry, INode, relation)
        self._add_bubbling_event(registry, INode, on_called, name="called")

        a = A()
        b = B(a)
        c = C(b)
        d = D(c)

        from pyramid_bubbling.components import RegistryAccess
        target = self._makeOne(RegistryAccess(registry))
        target.fire(d, "called")

        compare(called, [d, c, b, a])

    def test_it__default_event_and_each_event(self):
        from pyramid_bubbling.components import ParentFromInstance
        ## d -> c
        C = NodeFactory("C", "IC")
        D = NodeFactory("D", "ID")

        called = []
        def on_called(self):
            called.append(self)
        def on_called_double(self):
            called.append(self)
            called.append(self)

        registry = get_registry()
        def lookup_parent(self):
            return self.parent
        relation = ParentFromInstance(lookup_parent, None)
        self._add_bubbling_path(registry, INode, relation)
        self._add_bubbling_event(registry, INode, on_called, name="called")
        self._add_bubbling_event(registry, C, on_called_double, name="called")

        c = C()
        d = D(c)

        from pyramid_bubbling.components import RegistryAccess
        target = self._makeOne(RegistryAccess(registry))
        target.fire(d, "called")
        compare(called, [d, c, c])

    def test_not_connected(self):
        ## d -> c. b -> a
        from pyramid_bubbling.components import ParentFromInstance
        A = NodeFactory("A", "IA")
        B = NodeFactory("B", "IB")
        C = NodeFactory("C", "IC")
        D = NodeFactory("D", "ID")

        called = []
        registry = get_registry()
        def lookup_parent(self):
            return self.parent
        self._add_bubbling_path(registry, B, ParentFromInstance(lookup_parent, None))
        self._add_bubbling_path(registry, D, ParentFromInstance(lookup_parent, None))

        def on_called(self):
            called.append(self)
        self._add_bubbling_event(registry, INode, on_called, name="called")

        a = A()
        b = B(a)
        c = C(b)
        d = D(c)

        from pyramid_bubbling.components import RegistryAccess
        target = self._makeOne(RegistryAccess(registry))
        target.fire(d, "called")
        compare(called, [d, c])

    def test_multi_case(self):
        from pyramid_bubbling.components import ParentFromInstance
        A = NodeFactory("A", "IA")
        B = NodeFactory("B", "IB")
        C = NodeFactory("C", "IC")
        D = NodeFactory("D", "ID")


        ## [bar] d -> b -> a
        ## [foo] d -> c -> b

        ## bar
        bar = []
        def on_bar(self):
            bar.append(self)

        registry = get_registry()
        def lookup_parent(self):
            return self.parent

        self._add_bubbling_path(registry, B, ParentFromInstance(lookup_parent, None), name="bar")
        self._add_bubbling_path(registry, D, ParentFromInstance(lambda s : s.parent.parent, None), name="bar")

        self._add_bubbling_event(registry, D, on_bar, name="bar")
        self._add_bubbling_event(registry, B, on_bar, name="bar")
        self._add_bubbling_event(registry, A, on_bar, name="bar")

        a = A()
        b = B(a)
        c = C(b)
        d = D(c)

        from pyramid_bubbling.components import RegistryAccess
        target = self._makeOne(RegistryAccess(registry, name="bar"))
        target.fire(d, "bar")
        compare(bar, [d, b, a])

        ## foo
        foo = []
        def on_foo(self):
            foo.append(self)

        self._add_bubbling_path(registry, C, ParentFromInstance(lookup_parent, None), name="foo")
        self._add_bubbling_path(registry, D, ParentFromInstance(lookup_parent, None), name="foo")

        self._add_bubbling_event(registry, D, on_foo, name="foo")
        self._add_bubbling_event(registry, C, on_foo, name="foo")
        self._add_bubbling_event(registry, B, on_foo, name="foo")

        target = self._makeOne(RegistryAccess(registry, name="foo"))
        target.fire(d, "foo")
        compare(foo, [d, c, b])



if __name__ == '__main__':
    unittest.main()
