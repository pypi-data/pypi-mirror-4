# -*- coding:utf-8; tab-width:4; mode:python -*-


def add_prefix(prefix, items):
    return [prefix + i for i in items]


def convert_to_string(obj, encoding='utf-8'):
    assert isinstance(obj, (str, unicode)), type(obj)

    if isinstance(obj, unicode):
        return obj.encode(encoding, 'replace')

    return obj


# FIXME: add an example in the docstring
class TreeRender(object):
    '''generic tree renderer'''

    @classmethod
    def draw(cls, sequence, func, connector='', level=0, args=[]):
        retval = ''
        lon = len(sequence)
        for i, item in enumerate(sequence):
            brother = cls.norm_brother
            parent  = cls.norm_parent

            if lon == i + 1:
                brother = cls.last_brother
                parent  = cls.last_parent

            retval += func(item,
                           connector + parent,
                           connector + brother,
                           level + 1,
                           *args)

        return retval


class UTF_TreeRender(TreeRender):
    norm_brother = u'├─'
    last_brother = u'└─'
    norm_parent = u'│  '
    last_parent = u'   '


class ASCII_TreeRender(TreeRender):
    norm_brother = '+-'
    last_brother = '`-'
    norm_parent = '|  '
    last_parent = '   '


class Printable(object):
    def __repr__(self):
        return str(self)

    def __str__(self):
        return unicode(self).encode('utf-8', 'replace')

    def __unicode__(self):
        raise NotImplementedError
