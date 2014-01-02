# -*- coding:utf-8 -*-
from zope.interface import (
    providedBy,
)
from . import (
    Bubbling, 
    Accessor
)
from .components import (
    RegistryAccessForClass, 
    RegistryAccess
)

import logging
logger = logging.getLogger(__name__)

def get_bubbling(request, start_point, path_name=""):
    try:
        next(iter(providedBy(start_point)))
    except (StopIteration, TypeError):
        return Bubbling(Accessor(path_name))
    if isinstance(start_point, type):
        return Bubbling(RegistryAccessForClass(request.registry, path_name))
    else:
        return Bubbling(RegistryAccess(request.registry, path_name))
