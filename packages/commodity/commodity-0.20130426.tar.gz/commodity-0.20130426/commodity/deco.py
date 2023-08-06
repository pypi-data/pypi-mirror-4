# -*- coding:utf-8; tab-width:4; mode:python -*-


def tag(name):
    """Set the given function attribute:

    >>> @tag('hidden')
    ... def func(args):
    ...     pass
    ...
    >>> func.hidden
    True
    """

    def wrap(f):
        setattr(f, name, True)
        return f
    return wrap


def handle_exception(exception, handler):
    def wrap(func):
        def wrapped(*args, **kargs):
            try:
                return func(*args, **kargs)
            except exception:
                handler()

        return wrapped
    return wrap
