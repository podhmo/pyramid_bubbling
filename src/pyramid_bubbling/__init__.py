# -*- coding:utf-8 -*-

import operator as op
from zope.interface import implementer
from pyramid.exceptions import ConfigurationError

from .interfaces import (
    IBubbling, 
    IAccess
)


class BubblingConfigurationError(ConfigurationError):
    pass

class _Singleton(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<_Singleton {!r} at 0x{:x}>".format(self.name, id(self))
Stop = _Singleton("Stop")


@implementer(IAccess)
class Accessor(object):
    def __init__(self, k="__parent__"):
        self.k = k

    def exists(self, target):
        return hasattr(target, self.k)

    def access(self, target):
        return getattr(target, self.k, None)

    def get_notify(self, subject, case):
        method_name = "on_{}".format(case)
        return getattr(subject, method_name, None)

@implementer(IBubbling)
class Bubbling(object):
    def __init__(self, access=None):
        self.access = access or Accessor()

    def get_iterator(self, startpoint):
        target = startpoint
        yield target
        access = self.access
        while access.exists(target):
            target = access.access(target)
            yield target

    def get_bubbling_path_order(self, leaf):
        iterator = self.get_iterator(leaf)
        result = []
        for target in iterator:
            if target is None:
                break
            # if not isinstance(target, type):
            #     raise BubblingConfigurationError("{} is not correct class".format(target))
            result.append(target)
        # if len(result) <= 1:
        #     raise BubblingConfigurationError("{} doesn't have bubbling relation".format(leaf))
        return result


    def get_ordered_event(self, startpoint, case, *args, **kwargs):
        iterator = self.get_iterator(startpoint)
        access = self.access

        for subject in iterator:
            notify = access.get_notify(subject, case)
            yield subject, notify

    def fire(self, startpoint, case, *args, **kwargs):
        assert isinstance(case, str)
        iterator = self.get_iterator(startpoint)
        access = self.access

        for subject in iterator:
            notify = access.get_notify(subject, case)
            if callable(notify):
                status = notify(subject, *args, **kwargs)
                if status is Stop:
                    break


class BubblingAttribute(property):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super(BubblingAttribute, self).__init__(*args, **kwargs)

    def __get__(self, wrapper, type_):
        if wrapper is None:
            return self.parent
        else:
            return super(BubblingAttribute, self).__get__(wrapper, type_)


def bubbling_attribute(parent_class):
    def _(method):
        return BubblingAttribute(parent_class, method)
    return _

def bubbling_attribute_factory(parent_class, attr):
    if isinstance(attr, str):
        return BubblingAttribute(parent_class, op.attrgetter(attr))
    else:
        return BubblingAttribute(parent_class, attr)


def includeme(config):
    config.add_directive("add_bubbling_event", config.maybe_dotted(".components.add_bubbling_event"))
    config.add_directive("add_bubbling_path", config.maybe_dotted(".components.add_bubbling_path"))
    config.add_directive("verify_bubbling_path", config.maybe_dotted(".components.verify_bubbling_path"))
    config.add_directive("verify_bubbling_event", config.maybe_dotted(".components.verify_bubbling_event"))
