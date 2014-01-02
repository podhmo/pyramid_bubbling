# -*- coding:utf-8 -*-
from zope.interface.interface import InterfaceClass
from zope.interface import (
    implementedBy, 
    implementer
)

_repository = {}

def clean_dynamic_interface():
    global _repository
    _repository = {}

def dynamic_interface(type_):
    global _repository
    try:
        return _repository[type_]
    except KeyError:
        _repository[type_] = make_interface_on_the_fly(type_)
        return _repository[type_]

def make_interface_on_the_fly(cls):
    name = "I{}".format(cls.__name__)
    iface = InterfaceClass(name)
    implementer(iface)(cls)
    return iface

def iface_from_class(Class, dynamic=True, Exception=Exception):
    if isinstance(Class, InterfaceClass):
        return Class
    elif isinstance(Class, type) and dynamic:
        return dynamic_interface(Class)
    else:
        raise Exception("interface is not found from {}".format(Class))


# def iface_from_class(Class, dynamic=True, Exception=Exception):
#     try:
#         if isinstance(Class, InterfaceClass):
#             iface = Class
#         else:
#             iface = next(iter(implementedBy(Class)))
#     except StopIteration:
#         if dynamic:
#             iface = dynamic_interface(Class)
#         else:
#             raise Exception("interface is not found from {}".format(Class))
#     return iface

