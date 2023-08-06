#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2011 Alan Franzoni. APL 2.0 licensed.

from unittest import TestCase
from abc import abstractmethod

from ducktypes.function_copy import copy_raw_func_only, fully_copy_func


@abstractmethod
def example_func(a, b, c=1):
    return 1

class AbstractTestFunctionCopy(object):

    def test_function_wrapper_preserves_function_arg_count(self):
        wrapped = self.copy_func(example_func)
        self.assertEquals(3, wrapped.func_code.co_argcount)

    def test_function_wrapper_preserves_function_return_value(self):
        wrapped = self.copy_func(example_func)
        self.assertEquals(1, wrapped(1,2))

    def test_wrapped_func_is_actually_a_copy(self):
        wrapped = self.copy_func(example_func)
        wrapped.someattribute = 3
        self.assertFalse(getattr(example_func, "someattribute", False))


class TestRaw(AbstractTestFunctionCopy, TestCase):
    def setUp(self):
        self.copy_func = copy_raw_func_only

    def test_wrapped_function_is_never_abstract(self):
        wrapped = self.copy_func(example_func)
        self.assertFalse(getattr(wrapped, "__isabstractmethod__", False))


class TestCopyFuncFully(AbstractTestFunctionCopy, TestCase):
    def setUp(self):
        self.copy_func = fully_copy_func

    def test_wrapped_function_abstract_attributes_are_copied(self):
        wrapped = self.copy_func(example_func)
        self.assertTrue(wrapped.__isabstractmethod__)


