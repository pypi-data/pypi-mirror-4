# -*- coding:utf-8; tab-width:4; mode:python -*-

import os.path


def abs_dirname(path):
    """
    Return absolute path for the directory containing `path`
    >>> abs_dirname('test/some.py')
    '/home/john/devel/test'
    """
    return os.path.dirname(os.path.realpath(path))


def child_relpath(path, start='.'):
    """
    >>> os.getcwd()
    /home/user
    >>> child_relpath('/home/user/doc/last')
    'doc/last'
    >>> child_relpath('/usr/share/doc')
    '/usr/share/doc'
    """
    relpath = os.path.relpath(path, start=start)
    if '..' in relpath:
        return path

    return relpath


def get_parent(path):
    """
    >>> get_parent('/usr/share/doc')
    '/usr/share'
    """
    path = path.strip()
    if path.endswith("/"):
        path = path[:-1]
    return "/".join(path.split("/")[:-1]) or "/"


def resolve_path(fname, paths, find_all=False):
    '''
    Search 'fname' in the given paths and return the first full path
    that has the file. If 'find_all' is True it returns all matching paths.
    It always returns a list.
    '''
    retval = []
    for p in paths:
        path = os.path.join(p, fname)
        if os.path.exists(path):
            if not find_all:
                return [path]

            retval.append(path)

    return retval


def resolve_path_ancestors(fname, path, find_all=False):
    '''
    Search 'fname' in the given path and its ancestors. It returns the
    first full path that has the file. If 'find_all' is True it returns all
    matching paths. Always returns a list
    '''
    ancestors = []
    while path != os.sep:
        ancestors.append(path)
        path = os.path.dirname(path)

    return resolve_path(fname, ancestors, find_all)


def find_in_ancestors(fname, path):
    try:
        path = os.path.abspath(path)
        return os.path.dirname(resolve_path_ancestors(fname, path)[0])
    except IndexError:
        return None
