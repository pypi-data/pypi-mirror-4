# -*- coding: utf-8 -*-
# (C) 2011- Alan Franzoni
from unittest import TestCase
from ducktypes.annotate import annotate_f



class TestAnnotations(TestCase):
    def test_parameter_annotations(self):
        @annotate_f(param1="param1-ann", param2="param2-ann")
        def myfunc(param1, param2=None):
            pass

        self.assertEquals({"param1":"param1-ann",
                           "param2":"param2-ann"},
            myfunc.__annotations__)

    def test_return_value_annotations(self):
        @annotate_f("retvalue")
        def myfunc(param1, param2=None):
            pass

        self.assertEquals({"return":"retvalue"},
            myfunc.__annotations__)

    def test_annotation_chaining(self):
          @annotate_f("retvalue")
          @annotate_f(param1="param1-ann", param2="param2-ann")
          def myfunc(param1, param2=None):
              pass

          self.assertEquals({"return":"retvalue",
                             "param1":"param1-ann",
                           "param2":"param2-ann"},
                myfunc.__annotations__)

    def test_annotating_returns_a_new_func(self):
        def myfunc(param1):
            pass

        annotate_f("something")(myfunc)

        self.assertFalse(getattr(myfunc, "__annotations__", False))

    def test_annotating_fails_on_nonexisting_parameter(self):
        def myfunc(param1):
            pass

        self.assertRaises(ValueError, annotate_f(noparam=123), myfunc)

    def test_can_annotate_varargs(self):
        @annotate_f(args="a", kwargs="k")
        def myfunc(param1, *args, **kwargs):
            pass

        self.assertEquals({"args":"a", "kwargs":"k"},
            myfunc.__annotations__)
        


        

        
