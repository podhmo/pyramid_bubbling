# -*- coding:utf-8 -*-
import unittest
from testfixtures import compare

class BubblingAttributesTests(unittest.TestCase):
    def test_bubbling_attribute__just_access(self):
        from pyramid_bubbling import bubbling_attribute
        class Parent(object):
            pass

        class Child(object):
            def __init__(self, parent):
                self.parent = parent

            @bubbling_attribute(Parent)
            def __parent__(self):
                return self.parent

        self.assertEqual(Child.__parent__, Parent)

    def test_bubbling_attribute_factory__just_access(self):
        from pyramid_bubbling import bubbling_attribute_factory
        class Parent(object):
            pass

        class Child(object):
            def __init__(self, parent):
                self.parent = parent

            __parent__ = bubbling_attribute_factory(Parent, "parent")

        self.assertEqual(Child.__parent__, Parent)



def NodeFactory(name, base=object, parent=None, attribute_name="__parent__"):
    from pyramid_bubbling import bubbling_attribute

    def __init__(self, parent=None):
        self.parent = parent
    attrs = {"__init__": __init__}

    if parent:
        @bubbling_attribute(parent)
        def __parent__(self):
            return self.parent
        attrs["__parent__"] = __parent__
    return type(name, (base, ), attrs)

class BubblingOrderTests(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid_bubbling import Bubbling
        return Bubbling

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_it(self):
        ## d -> c -> b -> a
        A = NodeFactory("A")
        B = NodeFactory("B", parent=A)
        C = NodeFactory("C", parent=B)
        D = NodeFactory("D", parent=C)

        target = self._makeOne()
        result = target.get_bubbling_path_order(D)
        compare(result, [D, C, B, A])


    def test_if_not_connected(self):
        ## d -> c; b -> a
        A = NodeFactory("A")
        B = NodeFactory("B", parent=A)
        C = NodeFactory("C")
        D = NodeFactory("D", parent=C)

        target = self._makeOne()

        result = target.get_bubbling_path_order(D)
        compare(result, [D, C])

    def test_if_orphan(self):
        ## d
        D = NodeFactory("D")
        target = self._makeOne()
        result = target.get_bubbling_path_order(D)
        compare(result, [D])

class BubblingEventSelfTests(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid_bubbling import Bubbling
        return Bubbling

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_bound_event_is_not_found__raise_exception(self):
        from pyramid_bubbling import BubblingRuntimeException

        A = NodeFactory("A")
        a = A()

        target = self._makeOne()
        with self.assertRaises(BubblingRuntimeException):
            target.fire(a, "undefined_event")

    def test_it(self):
        ## d -> c -> b -> a
        ## event: [d, c, b, a]
        called = []
        def on_called(self, subject):
            called.append(self)
        A = NodeFactory("A")
        A.on_called = on_called
        B = NodeFactory("B", parent=A)
        B.on_called = on_called
        C = NodeFactory("C", parent=B)
        C.on_called = on_called
        D = NodeFactory("D", parent=C)
        D.on_called = on_called
        a = A()
        b = B(a)
        c = C(b)
        d = D(c)

        target = self._makeOne()
        target.fire(d, "called")

        compare(called, [d, c, b, a])

    def test_it__stop(self):
        ## routing order: d -> c -> b -> a
        ## event: [d]
        from pyramid_bubbling import Stop
        called = []
        def on_called__stop(self, subject):
            called.append(self)
            return Stop
        A = NodeFactory("A")
        A.on_called__stop = on_called__stop
        B = NodeFactory("B", parent=A)
        B.on_called__stop = on_called__stop
        C = NodeFactory("C", parent=B)
        C.on_called__stop = on_called__stop
        D = NodeFactory("D", parent=C)
        D.on_called__stop = on_called__stop
        a = A()
        b = B(a)
        c = C(b)
        d = D(c)

        target = self._makeOne()
        target.fire(d, "called__stop")

        compare(called, [d])

    def test_not_connected(self):
        ## d -> c. b -> a
        called = []
        def on_called(self, subject):
            called.append(self)
        A = NodeFactory("A")
        A.on_called = on_called
        B = NodeFactory("B", parent=A)
        B.on_called = on_called
        C = NodeFactory("C")
        C.on_called = on_called
        D = NodeFactory("D", parent=C)
        D.on_called = on_called
        a = A()
        b = B(a)
        c = C()
        d = D(c)

        target = self._makeOne()
        target.fire(d, "called")
        compare(called, [d, c])

    def test_multi_case(self):
        from pyramid_bubbling import Accessor, bubbling_attribute_factory
        ## [foo] d -> c -> b
        ## [bar] d -> b -> a
        bar = []
        def on_bar(self, subject):
            bar.append(self)
        foo = []
        def on_foo(self, subject):
            foo.append(self)
        A = NodeFactory("A")
        A.on_bar = on_bar
        B = NodeFactory("B", parent=A)
        B.__bar__ = bubbling_attribute_factory(A, "parent")
        B.on_foo = on_foo
        B.on_bar = on_bar
        C = NodeFactory("C")
        C.__foo__ = bubbling_attribute_factory(B, "parent")
        C.on_foo = on_foo
        D = NodeFactory("D", parent=C)
        D.__foo__ = bubbling_attribute_factory(C, "parent")
        D.__bar__ = bubbling_attribute_factory(B, "parent.parent")
        D.on_foo = on_foo
        D.on_bar = on_bar

        a = A()
        b = B(a)
        c = C(b)
        d = D(c)

        target_foo = self._makeOne(Accessor("__foo__"))
        target_foo.fire(d, "foo")
        compare(foo, [d, c, b])

        target_bar = self._makeOne(Accessor("__bar__"))
        target_bar.fire(d, "bar")
        compare(bar, [d, b, a])

if __name__ == '__main__':
    unittest.main()
