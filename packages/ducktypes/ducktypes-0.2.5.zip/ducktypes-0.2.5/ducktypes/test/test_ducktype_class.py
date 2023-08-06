#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf8

from unittest import TestCase

from abc import ABCMeta, abstractmethod
from ducktypes.ducktype import Duck, DuckABCMeta, DuckABCMetaFromABC

class Empty(object):
    pass

class SomeClass(object):
    def someMethod(self, a, b):
        pass

    def otherMethod(self):
        pass

basic_ducktype = Duck.from_class(SomeClass)

class OtherClass(object):
    def someMethod(self, a, b):
        pass

    def otherMethod(self):
        pass


class TestDuckTypesFromClass(TestCase):
    def test_otherclass_instance_is_compatible_with_ducktype(self):
        myobj = OtherClass()
        basic_ducktype.verify_implemented_by(myobj)

    def test_empty_is_not_compatible_with_ducktype(self):
        myobj = Empty()
        self.assertFalse(basic_ducktype.maybe_implemented_by(myobj))

class SomeABC(SomeClass):
    __metaclass__ = ABCMeta

    @abstractmethod
    def otherMethod(self):
        pass


abc_ducktype = Duck.from_class(SomeABC)

class TestDuckTypesFromABC(TestCase):
    def test_otherclass_instance_is_compatibile_with_abctype(self):
        myobj = OtherClass()
        abc_ducktype.verify_implemented_by(myobj)

    def test_empty_is_not_compatibile_with_abctype(self):
        myobj = Empty()
        self.assertFalse(abc_ducktype.maybe_implemented_by(myobj))

class DuckEnabledABC(SomeClass):
    __metaclass__ = DuckABCMeta
    @abstractmethod
    def someMethod(self, a, b):
        pass


class TestDuckEnabledABC(TestCase):
    def test_duck_enabled_ABC_is_abstract(self):
        self.assertRaises(TypeError, DuckEnabledABC)

    def test_duck_enabled_ABC_offers_duck_isinstance_check(self):
        self.assertTrue(isinstance(OtherClass(), DuckEnabledABC))

class TestDuckEnabledABCfromPlainABC(TestCase):
    def test_duckenabled_ABC_offers_duck_isinstance_check(self):
        self.assertTrue(isinstance(OtherClass(), DuckABCMetaFromABC(SomeABC)))

    def test_non_duckenabled_ABC_doest_pass_duck_isinstance_check(self):
        self.assertFalse(isinstance(OtherClass(), SomeABC))


