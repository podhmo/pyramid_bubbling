
pyramid_bubbling
================

bubbling event

sample
----------------------------------------

output ::

    ----------------click------------------------
    [('button', '3'), ('area', '2'), ('document', '1')]
    (<models.Button object at 0x107281ed0>, <function on_click_button at 0x10722c050>)
    (<models.Area object at 0x107281750>, <function on_click_area at 0x107225ef0>)
    (<models.Document object at 0x107281b10>, <function on_click_document at 0x10720b710>)
    ----------------tap------------------------
    [('tap', '3'), ('tap', '2'), ('tap', '1')]
    (<models.Button object at 0x107281ed0>, <function on_tap at 0x10722c170>)
    (<models.Area object at 0x107281750>, <function on_tap at 0x10722c170>)
    (<models.Document object at 0x107281b10>, <function on_tap at 0x10722c170>)

demo/main.py
::

    # -*- coding:utf-8 -*-
    from pyramid.testing import testConfig, DummyRequest
    from pyramid_bubbling.components import ParentFromInstance
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    from models import (
        Document,
        Area,
        Button
    )
    
    with testConfig() as config:
        config.include("pyramid_bubbling")
        config.add_bubbling_path(Area, ParentFromInstance(
            lambda s: s.document,
            lambda c: Document
        ))
        config.add_bubbling_path(Button, ParentFromInstance(
            lambda s: s.area,
            lambda c: Area
        ))
    
        config.scan("models")
        config.verify_bubbling_path(Button, [Button, Area, Document])
        config.verify_bubbling_event(Button, "click")
    
    
        def make_request():
            return DummyRequest(config.registry)
    
    
        doc = Document("1")
        area = Area("2", document=doc)
        button = Button("3", area=area)
    
        from pyramid_bubbling.api import get_bubbling
    
        request = make_request()
        bubbling = get_bubbling(request, button)
    
    
        ## click
        print("----------------click------------------------")
        result = []
        bubbling.fire(button, "click", result)
    
        assert result == [('button', '3'), ('area', '2'), ('document', '1')]
        print(result)
        for x in bubbling.get_ordered_event(button, "click"):
            print(x)
    
    
        ## tap
        print("----------------tap------------------------")
        result = []
        bubbling.fire(button, "tap", result)
        assert result == [('tap', '3'), ('tap', '2'), ('tap', '1')]
        print(result)
        for x in bubbling.get_ordered_event(button, "tap"):
            print(x)
    
    
demo/models.py
::

    # -*- coding:utf-8 -*-
    from pyramid_bubbling.components import bubbling_event_config
    
    from zope.interface import Interface, implementer
    
    class INode(Interface):
        pass
    
    @implementer(INode)
    class Node(object):
        pass
    
    class Document(Node):
        def __init__(self, name):
            self.name = name
    
    class Area(Node):
        def __init__(self, name, document):
            self.name = name
            self.document = document
    
    class Button(Node):
        def __init__(self, name, area):
            self.name = name
            self.area = area
    
    @bubbling_event_config(Document, "click")
    def on_click_document(subject, result):
        result.append(("document", subject.name))
    
    @bubbling_event_config(Area, "click")
    def on_click_area(subject, result):
        result.append(("area", subject.name))
    
    @bubbling_event_config(Button, "click")
    def on_click_button(subject, result):
        result.append(("button", subject.name))
    
    @bubbling_event_config(INode, "tap")
    def on_tap(subject, result):
        result.append(("tap", subject.name))
