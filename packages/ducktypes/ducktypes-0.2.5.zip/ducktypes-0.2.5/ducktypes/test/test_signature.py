#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf8

from unittest import TestCase

from ducktypes.signature import is_signature_compatible


def two_arg_callable1(a, b):
    pass

def two_arg_callable_2(a, b):
    pass

def two_arg_one_optarg_callable(a, b, c=None):
    pass

def two_arg_one_optarg_callable_other(a, b, d=None):
    pass

def three_arg_callable(a, b, c):
    pass

def two_optarg_callable(a=None, b=None):
    pass

def three_optarg_callable(a=None, c=None, b=None):
    pass

def two_optarg_callable_switched(b=None, a=None):
    pass

def all_kwargs_callable(**kwargs):
    pass

def optarg_kwargs_callable(b=None, **kwargs):
    pass

def arg_optarg_kwargs_callable(a, b=None, **kwargs):
    pass

def varargs_kwargs_callable(*args, **kwargs):
    pass

def all_varargs_callable(*args):
    pass

def three_args_varargs_callable(a, b, c, *args):
    pass

def empty_callable():
    pass

def mixed_everything_callable(a, b=None, *args, **kwargs):
    pass

#categorized funcs for better test organization.
everything = [value for name, value in locals().items() if "callable" in name]

# TODO: strict argument checking
# TODO: data-driven test-refactor, test everything against everything.

class TestVarargsKwargsSignature(TestCase):
    def test_every_func_compatible_with_varargs_kwargs(self):
        for func in everything:
            self.assertEquals(True, is_signature_compatible(func, varargs_kwargs_callable) )

    def test_vararg_kwargs_incompatible_with_everything_but_itself(self):
        everything_but_varargs_kwargs_callable = filter(lambda x: x.func_name != "varargs_kwargs_callable", everything)
        for func in everything_but_varargs_kwargs_callable:
            self.assertEquals(False, is_signature_compatible(varargs_kwargs_callable, func), "%s is compatible!" % func.func_name)

    def test_three_arg_optarg_callable_compatible_with_mixed_everything_callable(self):
        self.assertEquals(False, is_signature_compatible(three_optarg_callable, mixed_everything_callable))

    def test_two_arg_one_optarg_callable_compatible_with_mixed_everything_callable(self):
        self.assertEquals(True, is_signature_compatible(two_arg_one_optarg_callable, mixed_everything_callable))

    def test_arg_optarg_kwargs_callable_compatible_with_mixed_everything_callable(self):
        self.assertEquals(True, is_signature_compatible(arg_optarg_kwargs_callable, mixed_everything_callable))


class TestKeywordArgumentsKwargsSignature(TestCase):
    def test_all_optargs_compatible_with_kwargs_only(self):
        self.assertEquals(True, is_signature_compatible(two_optarg_callable, all_kwargs_callable))

    def test_optarg_kwargs_compatibile_with_kwargs_only(self):
        self.assertEquals(True, is_signature_compatible(optarg_kwargs_callable, all_kwargs_callable))

    def test_arg_optarg_kwargs_compatibile_with_kwargs_only(self):
        self.assertEquals(True, is_signature_compatible(arg_optarg_kwargs_callable, all_kwargs_callable))

    def test_kwargs_compatible_with_kwargs(self):
        self.assertEquals(True, is_signature_compatible(all_kwargs_callable, all_kwargs_callable))

    def test_kwargs_compatible_with_optarg_kwargs(self):
        self.assertEquals(True, is_signature_compatible(all_kwargs_callable, optarg_kwargs_callable))

    def test_kwargs_not_compatible_with_arg_optarg_kwargs(self):
        self.assertEquals(False, is_signature_compatible(all_kwargs_callable, arg_optarg_kwargs_callable))

class TestKeywordArgumentsNonKwargsSignature(TestCase):
    def test_different_optarg_names_are_not_compatible(self):
        self.assertEquals(False, is_signature_compatible(two_arg_one_optarg_callable,
                                                         two_arg_one_optarg_callable_other))
    # is this a candidate for strict checking?
    # TODO: strick checking mode.
    def test_switched_optional_args_retain_compatibility(self):
        self.assertEquals(True, is_signature_compatible(two_optarg_callable, two_optarg_callable_switched))

    def test_three_arg_callable_compatible_with_optarg_callable_with_same_names(self):
        self.assertEquals(True, is_signature_compatible(three_arg_callable, two_arg_one_optarg_callable))

    def test_three_arg_callable_compatible_with_optarg_callable_with_diff_names(self):
        self.assertEquals(True, is_signature_compatible(three_arg_callable, two_arg_one_optarg_callable_other))

    def test_optarg_callable_is_not_compatible_with_three_arg_callable_with_same_names(self):
        self.assertEquals(False, is_signature_compatible(two_arg_one_optarg_callable, three_arg_callable))

    def test_two_optarg_callable_compatible_with_three_optarg_callable_same_names(self):
        self.assertEquals(True, is_signature_compatible(two_optarg_callable, three_optarg_callable))

    def test_three_optarg_callable_not_compatible_with_two_optarg_callable_same_names(self):
        self.assertEquals(False, is_signature_compatible(three_optarg_callable, two_optarg_callable))


class TestPositionalNonVarArgumentsSignature(TestCase):
    def test_identical_signatures_are_compatible(self):
        self.assertEquals(True, is_signature_compatible(two_arg_callable1, two_arg_callable_2))

    def test_optional_arg_keeps_signature_compatible(self):
        self.assertEquals(True, is_signature_compatible(two_arg_callable1, two_arg_one_optarg_callable))

    def test_maybe_three_arg_signature_is_incompatible_with_two(self):
        self.assertEquals(False, is_signature_compatible(two_arg_one_optarg_callable, two_arg_callable1))

    def test_three_arg_sig_incompatible_with_two(self):
        self.assertEquals(False, is_signature_compatible(three_arg_callable, two_arg_callable1))

    def test_two_arg_sig_incompatible_with_three(self):
        self.assertEquals(False, is_signature_compatible(two_arg_callable1, three_arg_callable))

    def test_two_arg_optarg_incompatible_with_three(self):
        self.assertEquals(False, is_signature_compatible(two_arg_one_optarg_callable, three_arg_callable))

    def test_three_arg_is_compatible_with_two_arg_optarg(self):
        self.assertEquals(True, is_signature_compatible(three_arg_callable, two_arg_one_optarg_callable))

    def test_two_arg_is_compatible_with_two_optarg(self):
        self.assertEquals(True, is_signature_compatible(two_arg_callable1, two_optarg_callable))

    def test_two_optarg_is_not_compatible_with_two_arg(self):
        self.assertEquals(False, is_signature_compatible( two_optarg_callable, two_arg_callable1))


class TestPositionalWithVarArgsSignature(TestCase):
    def test_any_fixed_arg_compatible_with_all_varargs(self):
        self.assertEquals(True, is_signature_compatible(two_arg_callable1, all_varargs_callable))

    def test_two_fixed_args_incompatible_three_args_varargs(self):
        self.assertEquals(False, is_signature_compatible(two_arg_callable1, three_args_varargs_callable))

    def test_empty_is_compatible_with_all_varargs(self):
        self.assertEquals(True, is_signature_compatible(empty_callable, all_varargs_callable))

    def test_all_varargs_is_not_compatibile_with_empty(self):
        self.assertEquals(False, is_signature_compatible(all_varargs_callable, empty_callable))

    def test_all_varargs_is_compatibile_with_all_varargs(self):
        self.assertEquals(True, is_signature_compatible(all_varargs_callable, all_varargs_callable))

    def test_three_args_varargs_is_compatible_with_all_varargs(self):
        self.assertEquals(True, is_signature_compatible(three_args_varargs_callable, all_varargs_callable))

    def test_three_args_varargs_is_compatible_with_three_args_varargs(self):
        self.assertEquals(True, is_signature_compatible(three_args_varargs_callable, three_args_varargs_callable))

    def test_all_varargs_is_not_compatibile_with_three_args_varargs(self):
        self.assertEquals(False, is_signature_compatible(all_varargs_callable, three_args_varargs_callable))

class DifferentMethods(object):
    @staticmethod
    def staticmeth(a, b, c):
        pass

    # this is not the drug you're looking for
    @classmethod
    def classmeth(cls, a, b, c):
        pass

    def instancemeth(self, a, b, c):
        pass



class TestStaticMethodCompatibility(TestCase):
    def setUp(self):
        self.obj = DifferentMethods()
        self.obj.attrfunc = lambda a, b, c: None

    def test_static_signature_is_compatible_with_obj_class_sig(self):
        self.assertTrue(is_signature_compatible(self.obj.staticmeth, self.obj.classmeth))

    def test_static_signature_is_compatible_with_cls_class_sig(self):
        self.assertTrue(is_signature_compatible(self.obj.staticmeth, DifferentMethods.classmeth))

    def test_static_signature_is_compatible_with_obj_instance_method(self):
        self.assertTrue(is_signature_compatible(self.obj.staticmeth, self.obj.instancemeth))

    def test_static_signature_is_not_compatible_with_class_unbound_method(self):
        self.assertFalse(is_signature_compatible(self.obj.staticmeth, DifferentMethods.instancemeth))

    def test_static_signature_is_compatible_with_static_signature(self):
        self.assertTrue(is_signature_compatible(self.obj.staticmeth, DifferentMethods.staticmeth))

    def test_static_signature_is_compatible_with_attrfunc(self):
        self.assertTrue(is_signature_compatible(self.obj.staticmeth, self.obj.attrfunc))

class TestClassMethodCompatibilityAsClass(TestCase):
    def setUp(self):
        self.obj = DifferentMethods()
        self.obj.attrfunc = lambda a, b, c: None
        
    def test_classmethod_signature_is_compatible_with_obj_class_sig(self):
        self.assertTrue(is_signature_compatible(DifferentMethods.classmeth, self.obj.classmeth))

    def test_classmethod_signature_is_compatible_with_obj_instance_method(self):
        self.assertTrue(is_signature_compatible(DifferentMethods.classmeth, self.obj.instancemeth))

class TestUnboundMethodsCompatibility(TestCase):
    def setUp(self):
        self.obj = DifferentMethods()
        self.obj.attrfunc = lambda a, b, c: None

    def test_unbound_method_not_compatible_with_bound(self):
        self.assertFalse(is_signature_compatible(DifferentMethods.instancemeth, self.obj.instancemeth))

    def test_unbound_method_not_compatible_with_static(self):
        self.assertFalse(is_signature_compatible(DifferentMethods.instancemeth, self.obj.staticmeth))


class BoundWithoutSelf(object):
    def instancemeth(*args):
        pass

    @staticmethod
    def staticmeth(*args):
        pass


class TestBoundMethodsCompatibility(TestCase):
    def setUp(self):
        self.obj = BoundWithoutSelf()
        self.obj.attrfunc = lambda a, b, c: None

    def test_bound_method_without_self_is_compatible_with_static(self):
        self.assertTrue(is_signature_compatible(self.obj.instancemeth, BoundWithoutSelf.staticmeth))

    def test_bound_method_without_self_is_compatible_with_unbound(self):
        self.assertTrue(is_signature_compatible(self.obj.instancemeth, BoundWithoutSelf.staticmeth))

    def test_classmethod_signature_is_not_compatible_with_class_unbound_method(self):
        self.assertFalse(is_signature_compatible(DifferentMethods.classmeth, DifferentMethods.instancemeth))

    def test_classmethod_signature_is_compatible_with_classmethod_signature(self):
        self.assertTrue(is_signature_compatible(DifferentMethods.classmeth, DifferentMethods.staticmeth))

    def test_classmethod_signature_is_compatible_with_attrfunc(self):
        self.assertTrue(is_signature_compatible(DifferentMethods.classmeth, self.obj.attrfunc))

class TestClassMethodCompatibilityAsObj(TestCase):
    def setUp(self):
        self.obj = DifferentMethods()
        self.obj.attrfunc = lambda a, b, c: None

    def test_classmethod_signature_is_compatible_with_obj_class_sig(self):
        self.assertTrue(is_signature_compatible(self.obj.classmeth, self.obj.classmeth))

    def test_classmethod_signature_is_compatible_with_obj_instance_method(self):
        self.assertTrue(is_signature_compatible(self.obj.classmeth, self.obj.instancemeth))

    def test_classmethod_signature_is_not_compatible_with_class_unbound_method(self):
        self.assertFalse(is_signature_compatible(self.obj.classmeth, DifferentMethods.instancemeth))

    def test_classmethod_signature_is_compatible_with_classmethod_signature(self):
        self.assertTrue(is_signature_compatible(self.obj.classmeth, DifferentMethods.staticmeth))

    def test_classmethod_signature_is_compatible_with_attrfunc(self):
        self.assertTrue(is_signature_compatible(self.obj.classmeth, self.obj.attrfunc))


class TestInstanceMethodCompatibility(TestCase):
    def setUp(self):
        self.obj = DifferentMethods()
        self.obj.attrfunc = lambda a, b, c: None

    def test_instancemethod_signature_is_compatible_with_obj_class_sig(self):
        self.assertTrue(is_signature_compatible(self.obj.instancemeth, self.obj.classmeth))

    def test_instancemethod_signature_is_compatible_with_obj_instance_method(self):
        self.assertTrue(is_signature_compatible(self.obj.instancemeth, DifferentMethods.classmeth))

    def test_instancemethod_signature_is_not_compatible_with_class_unbound_method(self):
        self.assertFalse(is_signature_compatible(self.obj.instancemeth, DifferentMethods.instancemeth))

    def test_instancemethod_signature_is_compatible_with_instancemethod_signature(self):
        self.assertTrue(is_signature_compatible(self.obj.instancemeth, DifferentMethods.staticmeth))

    def test_instancemethod_signature_is_compatible_with_attrfunc(self):
        self.assertTrue(is_signature_compatible(self.obj.instancemeth, self.obj.attrfunc))


class TestAttrFuncCompatibility(TestCase):
    def setUp(self):
        self.obj = DifferentMethods()
        self.obj.attrfunc = lambda a, b, c: None

    def test_attrfunc_signature_is_compatible_with_obj_class_sig(self):
        self.assertTrue(is_signature_compatible(self.obj.attrfunc, self.obj.classmeth))

    def test_attrfunc_signature_is_compatible_with_obj_instance_method(self):
        self.assertTrue(is_signature_compatible(self.obj.attrfunc, DifferentMethods.classmeth))

    def test_attrfunc_signature_is_not_compatible_with_class_unbound_method(self):
        self.assertFalse(is_signature_compatible(self.obj.attrfunc, DifferentMethods.instancemeth))

    def test_attrfunc_signature_is_compatible_with_attrfunc_signature(self):
        self.assertTrue(is_signature_compatible(self.obj.attrfunc, DifferentMethods.staticmeth))

    def test_attrfunc_signature_is_compatible_with_instancemeth(self):
        self.assertTrue(is_signature_compatible(self.obj.attrfunc, self.obj.instancemeth))


class TestUnboundMethodsCompatibility(TestCase):
    # unbound methods are bad beasts and I don't know if this makes sense.
    def setUp(self):
        self.obj = DifferentMethods()
        self.obj.attrfunc = lambda a, b, c: None

    def test_unboundmethod_signature_is_not_compatible_with_obj_class_sig(self):
        self.assertFalse(is_signature_compatible(DifferentMethods.instancemeth, self.obj.classmeth))

    def test_unboundmethod_signature_is_not_compatible_with_obj_instance_method(self):
        self.assertFalse(is_signature_compatible(DifferentMethods.instancemeth, DifferentMethods.classmeth))

    def test_unboundmethod_signature_is_compatible_with_class_unbound_method(self):
        self.assertTrue(is_signature_compatible(DifferentMethods.instancemeth, DifferentMethods.instancemeth))

    def test_unboundmethod_signature_is_not_compatible_with_unboundmethod_signature(self):
        self.assertFalse(is_signature_compatible(DifferentMethods.instancemeth, DifferentMethods.staticmeth))

    def test_unboundmethod_signature_is_not_compatible_with_instancemeth(self):
        self.assertFalse(is_signature_compatible(DifferentMethods.instancemeth, self.obj.instancemeth))






        



