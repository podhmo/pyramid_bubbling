# -*- coding:utf-8 -*-
import venusian
import itertools
from zope.interface import (
    Interface,
    implementer,
    provider, 
    providedBy,
    implementedBy
)
from zope.interface.verify import verifyObject
from weakref import WeakValueDictionary
from . import (
    Bubbling, 
    BubblingConfigurationError
)
from .util import iface_from_class

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

@implementer(IAccess)
class RegistryAccess(object):
    def __init__(self, registry, name=""):
        self.registry = registry
        self.name = name
        self.cache = WeakValueDictionary()

    def _get_relation(self, target):
        try:
            fn = self.cache[target]
        except KeyError:
            fn = _lookup(self.registry, [providedBy(target)], name=self.name)
            if fn is None:
                return fn
            self.cache[target] = fn
        return fn

    def exists(self, target):
        ## todo: speedup if need.
        fn = self._get_relation(target)
        return bool(fn and fn(target))

    def access(self, target):
        fn = self._get_relation(target)
        return fn(target)

    def get_notify(self, target, name):
        return self.registry.adapters.lookup([providedBy(target)], IEvent, name=name)


@implementer(IAccess)
class RegistryAccessForClass(object):
    def __init__(self, registry, name=""):
        self.registry = registry
        self.name = name

    def lookup(self, target):
        return _lookup(self.registry, [implementedBy(target)], name=self.name)

    def exists(self, target):
        ## todo: speedup if need.
        fn = self.lookup(target)
        return bool(fn and fn.from_class(target))

    def access(self, target):
        return self.lookup(target).from_class(target)

    def get_notify(self, target, name):
        return self.registry.adapters.lookup([implementedBy(target)], IEvent, name=name)


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



def _add_bubbling_path(registry, ParentFromInstanceClass, parent_from_instance, name="", dynamic=True):
    verifyObject(IParentFromInstanceAdapter, parent_from_instance)
    iface = iface_from_class(ParentFromInstanceClass, dynamic=dynamic, Exception=BubblingConfigurationError)
    if not isinstance(iface, (list, tuple)):
        iface = [iface]
    registry.adapters.register(iface, IParentFromInstanceAdapter, name, parent_from_instance)

def add_bubbling_path(config, instanceClass, parent_from_instance, name=""):
    _add_bubbling_path(config.registry, config.maybe_dotted(instanceClass), parent_from_instance, name=name)

def _add_bubbling_event(registry, SubjectClass, fn, name="", dynamic=True):
    iface = iface_from_class(SubjectClass, dynamic=dynamic, Exception=BubblingConfigurationError)
    if not isinstance(iface, (list, tuple)):
        iface = [iface]
    fn = provider(IEvent)(fn)
    registry.adapters.register(iface, IEvent, name, fn)

def add_bubbling_event(config, SubjectClass, fn, name=""):
    _add_bubbling_event(config.registry, config.maybe_dotted(SubjectClass), fn, name=name)

def _lookup(registry, obj, name=""):
    return registry.adapters.lookup(obj, IParentFromInstanceAdapter, name=name)

def lookup(request, iface, name=""):
    return _lookup(request.registry, iface, name=name)

##
def bubbling_event_config(SubjectClass, name=""):
    def _(wrapped):
        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_bubbling_event(SubjectClass, wrapped, name=name)

        info = venusian.attach(wrapped, callback, category='pyramid')
        return wrapped
    return _

def verify_bubbling_path(config, startpoint, expected, name="", access=None):
    from pyramid.config.util import MAX_ORDER
    def register():
        bubbling = Bubbling(access or get_bubbling_registry_access(config, name))
        result = bubbling.get_bubbling_path_order(startpoint)
        if not (result == expected):
            raise BubblingConfigurationError("expected:{} != result:{}".format(expected, result))
    config.action(None, register, order=MAX_ORDER)

def verify_bubbling_event(config, startpoint, event_name="", path_name="", access=None):
    bubbling = Bubbling(access or get_bubbling_registry_access(config, path_name))
    r = []
    for subject, ev in bubbling.get_ordered_event(startpoint, event_name):
        if subject is None:
            break
        if ev is None:
            raise BubblingConfigurationError("subject={}, not bound event. registered event:({})".format(
                subject, 
                config.registry.adapters.lookupAll([implementedBy(startpoint)], IEvent)
            ))
        r.append(ev)
    return r

def get_bubbling_registry_access(config, path_name=""):
    return RegistryAccessForClass(config.registry, name=path_name)

