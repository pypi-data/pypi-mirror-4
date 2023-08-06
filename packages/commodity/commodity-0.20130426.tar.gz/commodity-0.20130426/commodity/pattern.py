# -*- coding:utf-8; tab-width:4; mode:python -*-
"""
.. module:: pattern
   :synopsis: Common pythonic design pattern

.. moduleauthor:: David Villa Alises <David.Villa@gmail.com>
"""

import collections
import string


# Borg pattern


from .type_ import checked_type

    # Exceptions
#    class ObserverException(Exception):
#        def __str__(self):
#            return "%s: %s" % (self.__class__.__name__, Exception.__str__(self))


def make_exception(name, message=''):
    return type(name, (Exception,), {})


class DummyLogger(object):
    def debug(self, *args):
        pass

    def warning(self, *args):
        pass


# class memoized2(object):
#     def __init__(self, func):
#         self.instance = None
#         self.func = func
#         self.cache = {}
#
#     def hash_args(self, *args, **kargs):
#         return cPickle.dumps((args, sorted(kargs.iteritems())))
#
#     def pack_args(self, args):
#         if self.instance is not None:
#             return (self.instance,) + args
#
#         return args
#
#     def __get__(self, instance, owner):
#         self.instance = instance
#         return self
#
#     def __call__(self, *args, **kargs):
#         _hash = self.hash_args(*args, **kargs)
#
#         if _hash not in self.cache:
#             self.cache[_hash] = self.func(*self.pack_args(args), **kargs)
#
#         return self.cache[_hash]
#
#     def repr(self):
#         return "memoized({0})".format(self.func)


class memoized(object):
    """Memoized decorator for funcions and class methods

    .. warning::

       Experimental, do not use in production code

    * http://pko.ch/2008/08/22/memoization-in-python-easier-than-what-it-should-be/
    * http://micheles.googlecode.com/hg/decorator/documentation.html
    """
    def __init__(self, func):
        self.instance = None
        self.func = func
        self.cache = {}

    def hash_args(self, *args, **kargs):
        if kargs:
            return args, frozenset(kargs.iteritems())

        return args

    def pack_args(self, args):
        if self.instance is None:
            return args

        return (self.instance,) + args

    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def __call__(self, *args, **kargs):
        key = self.hash_args(*args, **kargs)

        if key not in self.cache:
            self.cache[key] = self.func(*self.pack_args(args), **kargs)

        return self.cache[key]

    def repr(self):
        return "memoized({0})".format(self.func)


# EXPERIMENTAL, DO NOT USE IN PRODUCTION CODE
# from cached_property in http://wiki.python.org/moin/PythonDecoratorLibrary
class memoizedproperty(object):
    def __init__(self, method):
        self.method = method
        self.instance = None
        self.cache = {}

    def __get__(self, instance, owner):
        self.instance = instance
        if instance not in self.cache:
            self.cache[instance] = self.method(instance)

        return self.cache[instance]

    def reset(self):
        del self.cache[self.instance]


class Flyweight(type):
    '''Flyweight dessign pattern (for identical objects) as metaclass

    >>> class Sample(object):
    >>>     __metaclass__ = Flyweight
    >>>
    >>>     def __init__(self, key, [...]):
    >>>         [...]
    '''

    def __init__(cls, name, bases, dct):
        cls.__instances = {}
        type.__init__(cls, name, bases, dct)

    def __call__(cls, key, *args, **kw):
        instance = cls.__instances.get(key)
        if instance is None:
            instance = type.__call__(cls, key, *args, **kw)
            cls.__instances[key] = instance
        return instance


class Observable(object):
    InvalidObserver = make_exception('InvalidObserver', 'observer must be callable')
    NotSuchObserver = make_exception('NoSuckObserver')
    ObserverException = make_exception('ObserverExcepton')

    def __init__(self):
        self.observers = []

    def attach(self, observer):
        if not callable(observer):
            raise self.InvalidObserver()

        if observer in self.observers:
            return

        self.observers.append(observer)

    def detach(self, observer):
        try:
            self.observers.remove(observer)
        except ValueError:
            raise self.NotSuchObserver(observer)

    def notify(self, value):
        for observer in self.observers:
            try:
                observer(value)
            except Exception, ex:
                raise self.ObserverException(ex)


# http://books.google.es/books?id=9_AXCmGDiz8C&lpg=PA9&pg=PA34&redir_esc=y#v=onepage&q&f=false
class Bunch(dict):
    """It provides dict keys as attributes and viceversa

    >>> data = dict(ccc=2)
    >>> bunch = Bunch(data)
    >>> bunch.ccc
    2
    >>> bunch.ddd = 3
    >>> bunch['ddd']
    3
    >>> bunch['eee'] = 4
    >>> bunch.eee
    4
    """
    def __init__(self, *args, **kargs):
        super(Bunch, self).__init__(*args, **kargs)
        self.__dict__ = self

    def copy(self):
        return self.__class__(**self)

    def __repr__(self):
        items = []
        for key in self.keys():
            items.append("'%s': %s" % (key, repr(getattr(self, key))))

        return "Bunch({0})".format(str.join(', ', items))


class NestedBunch(Bunch):
    """Bunch with recursive fallback in other bunch (its parent)

    >>> a = NestedBunch()
    >>> a.foo = 1
    >>> a2 = b.new_layer()
    >>> a2.bar = 2
    >>> a2.foo
    1
    >>> a2.keys()
    ['foo', 'bar']

    >>> b = NestedBunch()
    >>> b.foo = 1
    >>> b2 = b.new_layer()
    >>> b2.foo
    1
    >>> b2['foo'] = 5000
    >>> b2.foo
    5000
    >>> b['foo']
    1

    >>> c = NestedBunch()
    >>> c.foo = 1
    >>> c2 = c.new_layer().new_layer()
    >>> c2.foo
    1
    """
    def __init__(self, *args, **kargs):
        super(NestedBunch, self).__init__(*args, **kargs)
        self.__parent = None

    def new_layer(self):
        retval = NestedBunch()
        retval.__parent = self
        return retval

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            if self.__parent is None:
                raise KeyError

            return getattr(self.__parent, key)

    def __getattr__(self, key):
        if self.__parent is None:
            raise AttributeError

        return self.__parent[key]

    def __dict_method(self, method):
        retval = []
        if self.__parent:
            retval.extend(getattr(self.__parent, method)())

        retval.extend(getattr(super(NestedBunch, self), method)())
        return retval

    def keys(self):
        retval = self.__dict_method('keys')
        retval.remove('_NestedBunch__parent')
        return retval

    def items(self):
        retval = self.__dict_method('items')
        retval.remove(('_NestedBunch__parent', self.__parent))
        return retval

    def values(self):
        retval = self.__dict_method('values')
        retval.remove(self.__parent)
        return retval


class MetaBunch(collections.MutableMapping):
    '''A bunch of bunches. It allows to recursively access keys as
       attributes and viceversa.  It may decorate any mapping type.

    >>> b = MetaBunch()
    >>> b['aaa'] = {'bbb': 1}
    >>> b.aaa.bbb
    1
    >>> b.aaa.ccc = 2
    >>> b['aaa']['ccc']
    2
   '''

    def __init__(self, dct=None):
        if dct is None:
            dct = dict()

        self.__dict__['dct'] = checked_type(collections.Mapping, dct)

    def __iter__(self):
        return iter(self.dct)

    def __len__(self):
        return len(self.dct)

    def __repr__(self):
        return repr(self.dct)

    def __getitem__(self, key):
        retval = self.dct

        for key in self.keypath(key):
            checked_type(collections.Mapping, retval)
            retval = retval[key]

        return retval

    def __setitem__(self, key, value):
        dct = self.dct
        keys = self.keypath(key)

        for key in keys[:-1]:
            if not key in dct:
                dct[key] = {}

            dct = dct[key]

        dct[keys[-1]] = value

    def __delitem__(self, key):
        dct = self.dct
        keys = self.keypath(key)

        for key in keys[:-1]:
            dct = dct[key]

        del dct[keys[-1]]

    def keypath(self, key):
        checked_type(str, key)
        return key.split('.')

    def __contains__(self, key):
        return self.has_key(key)

    def has_key(self, key):
        dct = self.dct

        try:
            for key in self.keypath(key):
                dct = dct[key]
        except (KeyError, TypeError):
            return False

        return True

    def __getattr__(self, attr):
        retval = self.__dict__['dct'][attr]
        if isinstance(retval, collections.Mapping) and \
                not isinstance(retval, MetaBunch):
            return MetaBunch(retval)

        return retval

    def __setattr__(self, attr, value):
        self[attr] = value


class TemplateBunch(collections.MutableMapping):
    """A Bunch automatically templated with its own content

    >>> t = TemplateBunch()
    >>> t.name = "Bob"
    >>> t.greeting = "Hi $name!"
    >>> t.greeting
    "Hi Bob!"
    >>> t.person = "$name's sister"
    >>> t.greeting = "Hi $person!"
    >>> t.person
    "Bob's sister"
    >>> t.greeting
    "Hi Bob's sister"
    """
    def __init__(self):
        self.__dict__['dct'] = Bunch()

    def __iter__(self):
        return iter(self.dct)

    def __len__(self):
        return len(self.dct)

    def __repr__(self):
        return repr(self.dct)

    def __delitem__(self, key):
        del self.dct[key]

    def has_key(self, key):
        return key in self.dct

    def __setattr__(self, attr, value):
        self.dct[attr] = value

    def __getattr__(self, attr):
        try:
            value = self.dct[attr]
        except KeyError:
            raise AttributeError(attr)

        if isinstance(value, (str, unicode)):
            return string.Template(value).safe_substitute(self)

        return value

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem__(self, key):
        try:
            return self.__getattr__(key)
        except AttributeError:
            raise KeyError(key)

    def clear(self):
        self.dct.clear()
