#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2011 Alan Franzoni. APL 2.0 licensed.

from inspect import getmembers, ismethod

from ducktypes.function_copy import copy_raw_func_only

def build_with_null_constructor(klass):
    # TODO: check overriden __new__!
    def null_init(self, *args, **kwargs):
        pass

    def null_new(cls, *args, **kwargs):
        return object.__new__(cls, *args, **kwargs)

    new_dict = {"__init__": null_init,
                "__new__": null_new,
                "__metaclass__": type}

    for name, value in [(name, value) for (name, value) in getmembers(klass, ismethod) if getattr(value, "__isabstractmethod__", False)] :
        new_dict[name] = copy_raw_func_only(value)

    return type(klass.__name__, (klass,), new_dict)()
  