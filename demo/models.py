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
