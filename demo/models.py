# -*- coding:utf-8 -*-
from pyramid_bubbling.components import bubbling_event_config

class Document(object):
    def __init__(self, name):
        self.name = name

class Area(object):
    def __init__(self, name, document):
        self.name = name
        self.document = document

class Node(object):
    def __init__(self, name, area):
        self.name = name
        self.area = area

@bubbling_event_config(Document, "click")
def on_click_document(subject, result):
    result.append(("document", subject.name))

@bubbling_event_config(Area, "click")
def on_click_area(subject, result):
    result.append(("area", subject.name))

@bubbling_event_config(Node, "click")
def on_click_node(subject, result):
    result.append(("node", subject.name))
