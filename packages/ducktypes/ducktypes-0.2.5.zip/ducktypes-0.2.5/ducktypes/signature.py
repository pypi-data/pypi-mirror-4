#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf8

from inspect import getargspec
from types import MethodType

#inspect.getargspec()
# inspect.getcallargs 2.7 only


# we'll need a better way to compare objects than signature very soon?
class NormalizedSignature(object):
    bound = True
    _unbound_class = None
    _func = None

    def __init__(self, callable_obj):
        argspec = getargspec(callable_obj)
        self.args = argspec.args
        self.varargs = argspec.varargs
        self.keywords = argspec.keywords
        self.defaults = argspec.defaults or ()

        # normalize if it's a bound method - the first parameter will
        # be already bound and doesn't matter.
        if isinstance(callable_obj, MethodType):
            # TODO: check what happens with args/varargs-only!
            self.bound = (callable_obj.im_self is not None)
            self._unbound_class = callable_obj.im_class
            self._func = callable_obj.im_func
            if self.bound:
                del self.args[0:1]

    @property
    def required_arg_count(self):
        return len(self.args) - len(self.defaults)

    @property
    def optional_arg_names(self):
        return set(self.args[self.required_arg_count:])


    def __eq__(self, other):
        if not other.bound and self.bound:
            # quick bailout. unbound methods are picky.
            return False

        if other.bound == self.bound == False:
            return issubclass(other._unbound_class, self._unbound_class) and (other._func == self._func)
        
        if self.varargs and not other.varargs:
            # finite always incompatible with infinite.
            return False

        if self.keywords and not other.keywords:
            # support-any-keyword always incompatible with support-just-some-keywords
            return False

        if not (other.varargs or other.keywords) and (len(self.args) > len(other.args)):
            return False


        # if arg names are available in reference and in testing, those should have a matching
        # name.
        if not other.keywords:
            for arg_name in self.optional_arg_names:
                if arg_name not in other.optional_arg_names:
                    return False

        return (self.required_arg_count) >= (other.required_arg_count)

def is_signature_compatible(reference, tested):
    """
    returns True if any mean of calling reference callable will allow tested callable to be called
    without raising TypeError; False otherwise.

    This doesn't consider runtime checks that might be done inside the method, just
    static method signature checking.
    """
    reference_sig = NormalizedSignature(reference)
    tested_sig = NormalizedSignature(tested)

    return reference_sig == tested_sig

