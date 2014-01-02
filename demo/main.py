# -*- coding:utf-8 -*-
from pyramid.testing import testConfig, DummyRequest
from pyramid_bubbling.components import ParentFromInstance
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from models import (
    Document, 
    Area, 
    Node
)

with testConfig() as config:
    config.include("pyramid_bubbling")
    config.add_bubbling_path(Area, ParentFromInstance(
        lambda s: s.document, 
        lambda c: Document
    ))
    config.add_bubbling_path(Node, ParentFromInstance(
        lambda s: s.area, 
        lambda c: Area
    ))

    config.scan("models")
    config.verify_bubbling_path(Node, [Node, Area, Document])
    config.verify_bubbling_event(Node, "click")


    def make_request():
        return DummyRequest(config.registry)


    doc = Document("1")
    area = Area("2", document=doc)
    node = Node("3", area=area)

    from pyramid_bubbling.api import get_bubbling

    request = make_request()
    bubbling = get_bubbling(request, node)
    result = []
    bubbling.fire(node, "click", result)

    assert result == [('node', '3'), ('area', '2'), ('document', '1')]

    ## 

    for x in bubbling.get_ordered_event(node, "click"):
        print(x)
