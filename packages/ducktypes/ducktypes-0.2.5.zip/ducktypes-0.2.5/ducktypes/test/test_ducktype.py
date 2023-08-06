#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf8

from unittest import TestCase

from ducktypes.ducktype import Duck

class Empty(object):
    pass

class SomeClass(object):
    def someMethod(self, a, b):
        pass

    def otherMethod(self):
        pass

basic_ducktype = Duck(SomeClass())

class OtherClass(object):
    def someMethod(self, a, b):
        pass

    def otherMethod(self):
        pass

class ClassWithMethodSameNameDifferentSignature(object):
    def someMethod(self):
        pass

    def otherMethod(self):
        pass

class ClassWithoutMatchingMethods(object):
    def xmethod(self):
        pass


class TestDuckTypes(TestCase):
    def test_mytype_is_compatible_with_ducktype(self):
        myobj = OtherClass()
        self.assertEquals(True, basic_ducktype.maybe_implemented_by(myobj))

    def test_othertype_is_not_compatible_with_ducktype(self):
        myobj = ClassWithMethodSameNameDifferentSignature()
        self.assertEquals(False, basic_ducktype.maybe_implemented_by(myobj))

    def test_thirdtype_is_not_compatible_with_ducktype(self):
        myobj = ClassWithoutMatchingMethods()
        self.assertEquals(False, basic_ducktype.maybe_implemented_by(myobj))

    def test_additional_methods_on_checked_object_dont_harm_comparison(self):
        class OtherClassWithAdditionalMethods(OtherClass):
            def additionalMethod(self, a):
                pass

        self.assertEquals(True, basic_ducktype.maybe_implemented_by(OtherClassWithAdditionalMethods()))



class SomeClassWithAPrivateMethod(SomeClass):
    def _private_method(self, a, b, c):
        pass

class SomeClassWithSpecialMethod(SomeClass):
    def __getitem__(self, item):
        pass

class SomeClassWithWrongSignatureInSpecialMethod(SomeClass):
    def __getitem__(self, item, a, b):
        pass

class OtherClassWithMatchingSpecialMethod(OtherClass):
    def __getitem__(self, item):
        pass

class OtherClassWithStaticSpecialMethod(OtherClass):
    @staticmethod
    def __getitem__(item):
        pass

class TestPrivateMethodsInDucks(TestCase):
    def test_private_methods_are_ignored_in_compatibility_check(self):
        myducktype = Duck(SomeClassWithAPrivateMethod())
        myobj = OtherClass()
        self.assertEquals(True, myducktype.maybe_implemented_by(myobj))

    def test_missing_special_method_makes_tested_object_not_compatibile(self):
        myducktype = Duck(SomeClassWithSpecialMethod())
        myobj = SomeClass()
        self.assertEquals(False, myducktype.maybe_implemented_by(myobj))

    def test_wrong_signature_special_method_not_compatibile(self):
        myducktype = Duck(SomeClassWithSpecialMethod())
        myobj = SomeClassWithWrongSignatureInSpecialMethod()
        self.assertEquals(False, myducktype.maybe_implemented_by(myobj))

    def test_matching_special_methods_compatible(self):
        myducktype = Duck(SomeClassWithSpecialMethod())
        myobj = OtherClassWithMatchingSpecialMethod()
        self.assertEquals(True, myducktype.maybe_implemented_by(myobj))

    def test_special_methods_dont_work_if_available_on_instance_only(self):
        myducktype = Duck(SomeClassWithSpecialMethod())
        myobj = Empty()
        myobj.__getitem__ = lambda item: None
        self.assertEquals(False, myducktype.maybe_implemented_by(myobj))

    def test_special_method_can_be_static(self):
        myducktype = Duck(SomeClassWithSpecialMethod())
        myobj = OtherClassWithStaticSpecialMethod()
        self.assertEquals(True, myducktype.maybe_implemented_by(myobj))

    def test_additional_special_methods_should_not_harm_comparison(self):
        class OtherClassWithAdditionalSpecialMethod(OtherClass):
            def __getitem__(self, item):
                pass

            def __setitem__(self, item, value):
                pass
        myducktype = Duck(SomeClassWithSpecialMethod())
        myobj = OtherClassWithAdditionalSpecialMethod()
        self.assertEquals(True, myducktype.maybe_implemented_by(myobj))





class OtherClassWithClassMethods(object):
    @classmethod
    def someMethod(cls, a, b):
        pass

    @classmethod
    def otherMethod(self):
        pass

class OtherClassWithStaticMethods(object):
    @staticmethod
    def someMethod(a, b):
        pass

    @staticmethod
    def otherMethod():
        pass

class OtherClassWithInnerClasses(object):
    @classmethod
    def someMethod(cls, a, b):
        pass


    class otherMethod(object):
        pass

    

    
class TestCallability(TestCase):
    def test_classmethod_same_callability_passes_compatibility_check(self):
        self.assertEquals(True, basic_ducktype.maybe_implemented_by(OtherClassWithClassMethods))

    def test_staticmethod_same_callability_passes_compatibility_check(self):
        basic_ducktype.verify_implemented_by(OtherClassWithStaticMethods)

    def test_empty_object_with_callables_passes_compatibility_check(self):
        empty = Empty()
        empty.someMethod = lambda a,b: None
        empty.otherMethod = lambda: None

        basic_ducktype.verify_implemented_by(empty)

    def test_inner_classes_pass_compatibility_check(self):
        basic_ducktype.verify_implemented_by(OtherClassWithStaticMethods)

