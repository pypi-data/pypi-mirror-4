# -*- coding:utf-8; tab-width:4; mode:python -*-

from unittest import TestCase

from commodity.testing import bind_method, assert_that, wait_that, call_with


class A(object):
    def __init__(self):
        self.n = 0

    def foo(self, arg):
        if self.n < 2:
            self.n += 1
            return 10

        return arg * 100

    def raise_exc(self, value):
        raise Exception


class bind_method_tests(TestCase):
    def test_one_call(self):
        assert_that(A(), bind_method(A.foo, args=(1,), result=10))

    def test_one_call_fail(self):
        try:
            assert_that(A(), bind_method(A.foo, args=(1,), result=102))
            self.fail()
        except AssertionError:
            pass

    def test_factory(self):
        foo = bind_method(A.foo)
        assert_that(A(), foo(args=(1,), result=10))

    def test_factory_fail(self):
        foo = bind_method(A.foo)
        try:
            assert_that(A(), foo(args=(1,), result=102))
            self.fail()
        except AssertionError:
            pass


class call_with_tests(TestCase):
    def test_wait_with_expected_value(self):
        a = A()
        wait_that(a.foo, call_with(1).returns(100), delta=0.1, timeout=1)

    def test_FAIL_wait_with_expected_value(self):
        a = A()
        try:
            wait_that(a.foo, call_with(1).returns(200), delta=0.1, timeout=1)
            self.fail()
        except AssertionError:
            pass

    def test_wait_no_exception(self):
        a = A()
        wait_that(a.foo, call_with(1), delta=0.1)

    def test_FAIL_wait_no_exception(self):
        a = A()
        try:
            wait_that(a.raise_exc, call_with(1), delta=0.1, timeout=1)
            self.fail()
        except AssertionError:
            pass
