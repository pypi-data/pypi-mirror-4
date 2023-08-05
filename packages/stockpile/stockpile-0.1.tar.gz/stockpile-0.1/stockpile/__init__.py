from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import importlib


def get_storage(name):
    modname, classname = name.split(":")
    mod = importlib.import_module(modname)
    return getattr(mod, classname)
