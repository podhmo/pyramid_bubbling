# -*- coding:utf-8 -*-
import unittest
from testfixtures import compare
from pyramid_bubbling import bubbling_attribute

class Document(object):
    def __init__(self, name):
        self.name = name

    def on_click(self, subject, result):
        result.append(("document", self.name))

class Area(object):
    def __init__(self, name, document):
        self.name = name
        self.document = document

    def on_click(self, subject, result):
        result.append(("area", self.name))

    @bubbling_attribute(Document)
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
        from pyramid_bubbling import (
            Bubbling, 
            Accessor
        )

        bubbling = Bubbling(access=Accessor("__parent__"))
        result = []
        bubbling.fire(self.item2, "click", result)

        compare(result, [("node", "item2"), ("area", "top"), ("document", "doc")])

    def test_stop(self):
        """click item2_ => bubbling: node, area[stop]"""

        from pyramid_bubbling import (
            Bubbling, 
            Accessor, 
            Stop
        )

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

if __name__ == '__main__':
    unittest.main()
