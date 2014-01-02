# -*- coding:utf-8 -*-
from zope.interface import (
    Interface,
)

class IParentFromInstanceAdapter(Interface):
    def __call__(instance):
        pass

    def from_class(cls):
        pass

class IBubbling(Interface):
    def get_iterator(startpoint):
        pass

    def get_bubbling_path_order(leaf):
        pass

    def fire(startpoint, case):
        pass


class IAccess(Interface):
    def exists(target):
        pass

    def access(target):
        pass

    def notify(subject, method_name, *args, **kwargs):
        pass

class IEvent(Interface):
    def __call__(subject, *args, **kwargs):
        pass

