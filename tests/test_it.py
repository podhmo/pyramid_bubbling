# -*- coding:utf-8 -*-
import unittest
from testfixtures import compare
from pyramid import testing
from pyramid_bubbling import bubbling_attribute

from zope.interface import Interface, implementer

class INode(Interface):
    pass

class Document(object):
    def __init__(self, name):
        self.name = name

    def on_click(self, subject, result):
        result.append(("document", self.name))

@implementer(INode)
class DocumentWithInterface(Document):
    pass

class Area(object):
    def __init__(self, name, document):
        self.name = name
        self.document = document

    def on_click(self, subject, result):
        result.append(("area", self.name))

    @bubbling_attribute(Document)
    def __parent__(self):
        return self.document

@implementer(INode)
class AreaWithInterface(Area):
    @bubbling_attribute(DocumentWithInterface)
    def __parent__(self):
        return self.document

class Node(object):
    def __init__(self, name, area):
        self.name = name
        self.area = area

    def on_click(self, subject, result):
        result.append(("node", self.name))

    @bubbling_attribute(Area)
    def __parent__(self):
        return self.area

@implementer(INode)
class NodeWithInterface(Node):
    @bubbling_attribute(AreaWithInterface)
    def __parent__(self):
        return self.area


def click_simple(subject, result):
    return result.append(subject.name)

def make_request(config):
    return testing.DummyRequest(registry=config.registry)

class SelfCaseIntegrationTests(unittest.TestCase):
    def setUp(self):
        """
        Document[doc]
          Area[top]
            Node[item1]
            Node[item2]
          Area[bottom]
            Node[item3]
        """
        self.doc = Document("doc")
        self.top = Area("top", self.doc)
        self.item1 = Node("item1", self.top)
        self.item2 = Node("item2", self.top)
        self.bottom = Area("bottom", self.doc)
        self.item3 = Node("item3", self.bottom)

    def test_it(self):
        """click item2 => bubbling: node, area, document"""
        from pyramid_bubbling import Bubbling, Accessor

        bubbling = Bubbling(access=Accessor("__parent__"))
        result = []
        bubbling.fire(self.item2, "click", result)

        compare(result, [("node", "item2"), ("area", "top"), ("document", "doc")])

    def test_stop(self):
        """click item2_ => bubbling: node, area[stop]"""
        from pyramid_bubbling import Bubbling, Accessor
        from pyramid_bubbling import Stop

        class StopArea(Area):
            def on_click(self, *args, **kwargs):
                super(StopArea, self).on_click(*args, **kwargs)
                return Stop

        top = StopArea("stop_top", self.doc)
        item2 = Node("stop_item2", top)
        bubbling = Bubbling(access=Accessor("__parent__"))
        result = []
        bubbling.fire(item2, "click", result)

        compare(result, [("node", "stop_item2"), ("area", "stop_top")])

    def test_configuration(self):
        """click item2 => bubbling: node, area, document"""
        from pyramid_bubbling import (
            Accessor
        )
        with testing.testConfig() as config:
            config.include("pyramid_bubbling")
            config.verify_bubbling_path(Node, [Node, Area, Document], access=Accessor("__parent__"))
            result = config.verify_bubbling_event(Node,  event_name="click", access=Accessor("__parent__"))
            compare(result, [Node.on_click, Area.on_click, Document.on_click])

class UseRegistryIntegrationTests(unittest.TestCase):
    def setUp(self):
        """
        Document[doc]
          Area[top]
            Node[item1]
            Node[item2]
          Area[bottom]
            Node[item3]
        """
        from pyramid_bubbling.components import ParentFromInstance

        self.doc = DocumentWithInterface("doc")
        self.top = AreaWithInterface("top", self.doc)
        self.item1 = NodeWithInterface("item1", self.top)
        self.item2 = NodeWithInterface("item2", self.top)
        self.bottom = AreaWithInterface("bottom", self.doc)
        self.item3 = NodeWithInterface("item3", self.bottom)

        ## config
        self.config = testing.setUp()
        self.config.include("pyramid_bubbling")

        def access(s):
            return getattr(s, "__parent__", None)
        self.config.add_bubbling_path(INode, ParentFromInstance(access, access))
        self.config.add_bubbling_event(INode, click_simple, "click")

    def tearDown(self):
        testing.tearDown()
        from pyramid_bubbling.util import clean_dynamic_interface
        clean_dynamic_interface()

    def test_it(self):
        """click item2 => bubbling: node, area, document"""
        from pyramid_bubbling.api import get_bubbling

        bubbling = get_bubbling(make_request(self.config), self.item2)
        result = []
        bubbling.fire(self.item2, "click", result)
        compare(result, ['item2', 'top', 'doc'])


    def test_stop(self):
        """click item2_ => bubbling: node, area[stop]"""

        from pyramid_bubbling import (
            Stop
        )
        from pyramid_bubbling.api import get_bubbling

        class StopArea(AreaWithInterface):
            pass

        def click_simple_stop(subject, result):
            click_simple(subject, result)
            return Stop

        self.config.add_bubbling_event(StopArea, click_simple_stop, "click")

        top = StopArea("stop_top", self.doc)
        item2 = NodeWithInterface("stop_item2", top)

        bubbling = get_bubbling(make_request(self.config), item2)
        result = []
        bubbling.fire(item2, "click", result)
        compare(result, ["stop_item2", "stop_top"])

    def test_configuration(self):
        """click item2 => bubbling: node, area, document"""
        config = self.config

        config.verify_bubbling_path(NodeWithInterface, [NodeWithInterface, AreaWithInterface, DocumentWithInterface])
        result = config.verify_bubbling_event(NodeWithInterface,  event_name="click")
        compare(result, [click_simple, click_simple, click_simple])

if __name__ == '__main__':
    unittest.main()
