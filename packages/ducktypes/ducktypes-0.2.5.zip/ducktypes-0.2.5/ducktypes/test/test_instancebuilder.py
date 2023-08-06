#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2011 Alan Franzoni. APL 2.0 licensed.

from unittest import TestCase
from abc import ABCMeta, abstractmethod

from ducktypes.instancebuilder import build_with_null_constructor
from ducktypes.ducktype import Duck


class SomeClass(object):

    
    def someMethod(self):
        pass

    def otherMethod(self, a, b):
        pass

class RaisingInit(SomeClass):
    __metaclass__ = ABCMeta

    def __init__(self):
        raise RuntimeError, "raising init was invoked"

    @abstractmethod
    def someMethod(self):
        pass

class RaisingNew(RaisingInit):
    def __new__(cls, *args, **kwargs):
        raise RuntimeError, "raising new was invoked"

class TestInstanceBuilder(TestCase):
    def test_when_using_build_null_constructor_init_is_not_invoked(self):
        build_with_null_constructor(RaisingInit)

    def test_when_using_build_null_constructor_new_is_not_invoked(self):
        build_with_null_constructor(RaisingNew)

    def test_built_object_is_an_instance_of_passed_class(self):
        built = build_with_null_constructor(RaisingInit)
        self.assertTrue(isinstance(built, RaisingInit))

    def test_built_object_has_compatibile_sig_with_someclass_instance(self):
        built = build_with_null_constructor(RaisingInit)
        duck = Duck(SomeClass())
        duck.verify_implemented_by(built)




  