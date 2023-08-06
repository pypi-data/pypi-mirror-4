#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2011 Alan Franzoni. APL 2.0 licensed.

from unittest import TestCase

from ducktypes.ducktype import Duck

# although those two objects will
# answer to the very same methods,
# only the first will be able
# to answer to len()


class LengthedType(object):
    def __len__(self):
        return 1

class FakeLengthedType(object):
    def __init__(self):
        self.__len__ = lambda: 1


class TestSpecialMethods(TestCase):

    def test_length(self):
        lengthed = LengthedType()
        fake = FakeLengthedType()

        myducktype = Duck(lengthed)

        self.assertEquals(False, myducktype.maybe_implemented_by(fake))
