# -*- coding:utf-8; tab-width:4; mode:python -*-

import time
import types

import hamcrest
from hamcrest.core.matcher import Matcher as hamcrest_Matcher
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.string_description import StringDescription
from hamcrest.core.assert_that import _assert_bool

from .str_ import Printable
from .type_ import checked_type
from .net import is_port_open, is_host_reachable


def assert_that(arg1, arg2=None, arg3=''):
    if isinstance(arg2, hamcrest_Matcher):
        _assert_match(actual=arg1, matcher=arg2, reason=arg3)
    else:
        _assert_bool(assertion=arg1, reason=arg2)


def _assert_match(actual, matcher, reason):
    if not matcher.matches(actual):
        description = StringDescription()
        description.append_text(reason)     \
            .append_description_of(matcher) \
            .append_text(', but ')
        matcher.describe_mismatch(actual, description)
        raise AssertionError(str(description))


def wait_that(actual, matcher, reason='', delta=1, timeout=5):
    exc = None
    init = time.time()
    timeout_reached = False
    while 1:
        try:
            if time.time() - init > timeout:
                timeout_reached = True
                break

            _assert_match(actual, matcher, reason)
            break

        except AssertionError as e:
            time.sleep(delta)
            exc = e

    if timeout_reached:
#        msg = '{0} was not true after {1} seconds'.format(matcher, timeout)
        raise exc


class Matcher(BaseMatcher):
    def describe_mismatch(self, item, mismatch_description):
        mismatch_description.append_text('it is not')


class Host(Printable):
    def __init__(self, name):
        self.name = checked_type(str, name)

    def __unicode__(self):
        return unicode(self.name)

localhost = Host('localhost')


class ListenPort(Matcher):
    def __init__(self, port, proto):
        self.port = checked_type(int, port)
        assert 0 < port < 65536
        self.proto = proto

    def _matches(self, item):
        self.host = checked_type(Host, item)
        return is_port_open(self.port, self.proto, self.host.name)

    def describe_to(self, description):
        description.append_text('port {0}/{1} to be open'.format(
                self.port, self.proto))

    def describe_mismatch(self, item, mismatch_description):
        mismatch_description.append_text('it is closed')


def listen_port(port, proto='tcp'):
    return ListenPort(port, proto)


class Reachable(Matcher):
    def _matches(self, host):
        self.host = checked_type(Host, host)
        return is_host_reachable(str(host))

    def describe_to(self, description):
        description.append_text("host is reachable")


def reachable():
    return Reachable()


#--------------------------

class MeetsImapQuery(Matcher):
    def __init__(self, criteria):
        self.criteria = criteria

    def _matches(self, mailbox):
        messages = mailbox.messages(self.criteria)
        if not messages:
            return False

        for m in messages:
            print m['Subject']

        return True

    def describe_to(self, description):
        description.append_text("some mail meet '%s'" % self.criteria)


def meets_imap_query(criteria):
    return MeetsImapQuery(criteria)


# experimental
# FIXME: deprecated, replace with bind_method without result
# class method_success(BaseMatcher):
#     def __init__(self, method):
#         # check it is an unbound method
#         self.method = method
#
#     def _matches(self, obj):
#         # check that obj type meets method type
#         return self.method(obj)
#
#     def describe_mismatch(self, item, mismatch_description):
#         mismatch_description.append_text('was False')
#
#     def describe_to(self, description):
#         description.append_text('{0} to be return True ')


class __nothing__(object):
    pass


#def is_unbound(method):
#    return method.im_self is None
#
#
#def get_unbound(method):
#    if is_unbound(method):
#        return method
#
#    return types.MethodType(method.im_func, None, method.im_class)


#class bind_method(BaseMatcher):
#    def __init__(self, method, args=(), kargs={}, result=__nothing__):
#        self.method = method
#        self.args = args
#        self.kargs = kargs
#        self.expected_result = result
#
#    def _matches(self, item):
#        assert isinstance(item, self.method.im_class)
#        self.actual_result = self.method(item, *self.args, **self.kargs)
#        if self.expected_result == __nothing__:
#            return True
#
#        return self.expected_result == self.actual_result
#
#    def __call__(self, args=(), kargs={}, result=__nothing__):
#        return bind_method(self.method, args=args, kargs=kargs, result=result)
#
#    def describe_to(self, description):
#        description.append_text(
#            '{0}.{1}({2}, {3}) expected to return {4}'.format(
#                self.method.im_class.__name__, self.method.im_func.__name__,
#                self.args, self.kargs, self.actual_result))
#
#    def describe_mismatch(self, item, description):
#        description.append_text('was %s' % self.expected_result)


class call_with(BaseMatcher):
    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs
        self.expected = __nothing__
        self.actual = None
        self.exc = None

    def returns(self, expected):
        self.expected = expected
        return self

    def _matches(self, func):
        self.func = func
        try:
            self.actual = self.func(*self.args, **self.kargs)
        except Exception as e:
            self.exc = e
            return False

        self.exc = None
        if self.expected is __nothing__:
            return True

        return hamcrest.is_(self.expected).matches(self.actual)

    def describe_to(self, description):
        description.append_text(
            '{0}({1}, {2}) expected to return {3}'.format(
                self.func, self.args, self.kargs, self.expected))

    def describe_mismatch(self, item, description):
        if self.exc is not None:
            description.append_text('raises %s' % self.exc)
        else:
            description.append_text('was %s' % self.actual)
