# -*- coding:utf-8 -*-
from zope.interface import (
    Interface,
    implementer,
    provider, 
    providedBy,
    implementedBy
)
from zope.interface.verify import verifyObject
from zope.interface.interface import InterfaceClass

class IParentFromInstanceAdapter(Interface):
    def __call__(instance):
        pass

    def from_class(cls):
        pass

class IBubbling(Interface):
    def get_iterator(startpoint):
        pass

    def get_bubbling_order(leaf):
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

@implementer(IAccess)
class RegistryAccess(object):
    IEventFace = IEvent
    def __init__(self, registry, name=""):
        self.registry = registry
        self.name = name

    def exists(self, target):
        ## todo: speedup if need.
        fn = _lookup(self.registry, providedBy(target), name=self.name)
        return bool(fn and fn(target))

    def access(self, target):
        return _lookup(self.registry, providedBy(target), name=self.name)(target)

    def get_notify(self, target, name):
        return self.registry.adapters.lookup([providedBy(target)], self.IEventFace, name=name)


@implementer(IAccess)
class RegistryAccessForClass(object):
    def __init__(self, registry, name=""):
        self.registry = registry
        self.name = name

    def exists(self, target):
        ## todo: speedup if need.
        fn = _lookup(self.registry, implementedBy(target), name=self.name)
        return bool(fn and fn.from_class(target))

    def access(self, target):
        return _lookup(self.registry, implementedBy(target), name=self.name).from_class(target)

@implementer(IParentFromInstanceAdapter)
class ParentFromInstance(object):
    def __init__(self, lookup, cls_lookup):
        self.lookup = lookup
        self.cls_lookup = cls_lookup

    def default_notify(self, *args, **kwargs):
        import sys
        sys.stderr.write("case:{}, args={}, kwargs={}".format(None, args, kwargs))
        return True

    def __call__(self, *args, **kwargs):
        return self.lookup(*args, **kwargs)

    def from_class(self, *args, **kwargs):
        return self.cls_lookup(*args, **kwargs)

import pyramid_bubbling
Bubbling = pyramid_bubbling.Bubbling
pyramid_bubbling.Bubbling = implementer(IBubbling)(Bubbling)
Accessor = pyramid_bubbling.Accessor
pyramid_bubbling.Accessor = implementer(IAccess)(Accessor)



def _register_parent_from_instance(registry, ParentFromInstanceClass, fn, name=""):
    verifyObject(IParentFromInstanceAdapter, fn)
    if isinstance(ParentFromInstanceClass, InterfaceClass):
        iface = ParentFromInstanceClass
    else:
        iface = implementedBy(ParentFromInstanceClass)
    registry.adapters.register([iface], IParentFromInstanceAdapter, name, fn)

def register_parent_from_instance(config, instanceClass, fn, name=""):
    _register_parent_from_instance(config.registry, config.maybe_dotted(instanceClass), fn, name=name)

def _register_routing_event(registry, SubjectClass, fn, name="", ievent_face=IEvent):
    if isinstance(SubjectClass, InterfaceClass):
        iface = SubjectClass
    else:
        iface = implementedBy(SubjectClass)
    registry.adapters.register([iface], ievent_face, name, provider(ievent_face)(fn))


def _lookup(registry, obj, name=""):
    return registry.adapters.lookup([obj], IParentFromInstanceAdapter, name=name)

def lookup(request, iface, name=""):
    return _lookup(request.registry, iface, name=name)
