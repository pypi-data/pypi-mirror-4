#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni. APL 2.0 licensed.
from abc import ABCMeta

import inspect
from ducktypes.signature import is_signature_compatible
from ducktypes.specialmethods import collections_classes
from ducktypes.instancebuilder import build_with_null_constructor

# those are available in just any newstyle instance.
o = object()
BUILTIN_OBJECT_METHOD_NAMES = [n for (n,m) in inspect.getmembers(o, callable)]
del o

METHOD_NAMES_TO_BE_IGNORED_IN_SIGNATURES = ["__metaclass__", "__instancecheck__", "__subclasscheck__"] + BUILTIN_OBJECT_METHOD_NAMES

class SignatureVerificationError(Exception):
    pass

class Duck(object):
    def __init__(self, reference_obj):
        self.reference_obj = reference_obj

    @classmethod
    def from_class(cls, reference_class):
        # TODO: this might not work if __getattr__ is employed on the class,
        # since it might need something that should get passed at init time.
        return cls(build_with_null_constructor(reference_class))

    def maybe_implemented_by(self, someobj):
        try:
            self.verify_implemented_by(someobj)
            return True
        except SignatureVerificationError:
            return False

    def verify_implemented_by(self, someobj):
        self._verify_public_methods(someobj)
        self._verify_special_methods(someobj)

    def _verify_public_methods(self, someobj):
        someobj_public_methods = self._fetch_public_methods(someobj)
        our_public_methods = self._fetch_public_methods(self.reference_obj)

        missing = set(our_public_methods).difference(set(someobj_public_methods))
        if missing:
            # someobj is lacking some method we need
            raise SignatureVerificationError, "%s lacks methods: %s" % (someobj, missing)

        for name, method in our_public_methods.items():
            if not is_signature_compatible(method, someobj_public_methods[name]):
                raise SignatureVerificationError, "%s signature for %s is incompatible" % (someobj, method)

    def _fetch_public_methods(self, obj):
        return dict(((method_name, method) for (method_name, method) in
                inspect.getmembers(obj, callable) if not method_name.startswith("_")))

# we should probably DOUBLE check???
    def _verify_special_methods(self, someobj):
        someobj_special_methods = self._fetch_special_methods(someobj)
        our_special_methods = self._fetch_special_methods(self.reference_obj)

        missing = set(our_special_methods).difference(set(someobj_special_methods))
        if missing:
            # someobj is lacking some method we need
            raise SignatureVerificationError, "%s lacks methods: %s" % (someobj, missing)

        for name, method in our_special_methods.items():
            if not is_signature_compatible(method, someobj_special_methods[name]):
                raise SignatureVerificationError, "%s signature for %s is incompatible" % (someobj, method)
       

    def _fetch_special_methods(self, obj):
        # it makes little sense to check builtin methods, even though
        # the subclass signature could be different.
        # TODO: check for overriden special methods wrong signatures.

        return dict(
            filter(lambda (n,m): (n not in METHOD_NAMES_TO_BE_IGNORED_IN_SIGNATURES),
                   ((method_name, method) for (method_name, method) in
                   inspect.getmembers(obj, callable) if self._is_special_method(obj, method_name)
                    )))

    def _is_special_method(self, obj, method_name):
        # TODO: edge case, what if parent has a different signature and gets overriden at
        # runtime on instance?
        parent = type(obj)
        return ( method_name.startswith("__") and method_name.endswith("__")
                 and getattr(parent, method_name, False))

class DuckABCMeta(ABCMeta):
    def __instancecheck__(cls, instance):
        duck = Duck.from_class(cls)
        return duck.maybe_implemented_by(instance)

def DuckABCMetaFromABC(abc_class):
    return DuckABCMeta("Duck" + abc_class.__name__, (abc_class,), {})


