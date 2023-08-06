# -*- coding: utf-8 -*-
# (C) 2011- Alan Franzoni
from ducktypes.function_copy import fully_copy_func

_NO_VALUE = object()


class SignatureAnnotator(object):
    """
    This is a PEP-3107 forward-compatibile annotator which
    can be used on Python 2.x.

    usage:

    SignatureAnnotator(return_value(optional), param_name=annotation_value,
        ...)(function_to_be_annotated) -> annotated_function

    varargs can be annotated by just using the very same name used for such
    argument, e.g. args and kwargs
    """
    def __init__(self, _return=_NO_VALUE, **kwargs):
        self.annotations = dict( (k,v) for (k,v) in kwargs.iteritems())
        self._return = _return

    def __call__(self, func):
        self._verify_named_params_in_func(func)
        func = fully_copy_func(func)
        self._update_func_annotations(func)
        return func

    def _verify_named_params_in_func(self, func):
        excess_annotations = set(self.annotations).difference(
            func.func_code.co_varnames)
        if excess_annotations:
            raise ValueError, "Annotating unknown args: {}".format(",".join(excess_annotations))

    def _update_func_annotations(self, func):
        if getattr(func, "__annotations__", _NO_VALUE) is _NO_VALUE:
            func.__annotations__ = {}
        func.__annotations__.update(self.annotations)
        if self._return != _NO_VALUE:
            func.__annotations__["return"] = self._return

# alias in order to match python's own name for pep-3107 "function annotations"
# while they're really "signature annotations" since they operate on parameters
# and return type names.
annotate_f = SignatureAnnotator