# -*- coding:utf-8 -*-

import operator as op
class BubblingConfigurationError(Exception):
    pass

class Accessor(object):
    def __init__(self, k="__parent__"):
        self.k = k

    def exists(self, target):
        return hasattr(target, self.k)

    def access(self, target):
        return getattr(target, self.k, None)

    def get_notify(self, subject, case):
        method_name = "on_{}".format(case)
        return getattr(subject, method_name)

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

    def get_bubbling_order(self, leaf):
        iterator = self.get_iterator(leaf)
        result = []
        for target in iterator:
            if not isinstance(target, type):
                raise BubblingConfigurationError("{} is not correct class".format(target))
            result.append(target)
        if len(result) <= 1:
            raise BubblingConfigurationError("{} doesn't have bubbling relation".format(leaf))
        return result

    def fire(self, startpoint, case, *args, **kwargs):
        iterator = self.get_iterator(startpoint)
        access = self.access

        for subject in iterator:
            notify = access.get_notify(subject, case)
            if callable(notify):
                notify(subject, *args, **kwargs)


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

