
""" The ``collections`` module  contains types and functions that define
    various collections and algorithms.
"""

import struct
import zlib

from wheezy.core.comp import defaultdict
from wheezy.core.comp import ntob


GZIP_HEADER = ntob('\x1F\x8B\x08\x00\x00\x00\x00\x00\x02\xFF', 'latin1')
MAX_INT = int('FFFFFFFF', 16)


def first_item_adapter(adaptee):
    """ Adapts ``defaultdict(list)``.__getitem__ accessor to
        return the first item from the list.

        >>> d = defaultdict(list)
        >>> d['a'].extend([1, 2, 3])
        >>> a = first_item_adapter(d)

        Return a first item from the list.

        >>> a['a']
        1
    """
    return ItemAdapter(adaptee, 0)


def last_item_adapter(adaptee):
    """ Adapts ``defaultdict(list)``.__getitem__ accessor to
        return the last item from the list.

        >>> d = defaultdict(list)
        >>> d['a'].extend([1, 2, 3])
        >>> a = last_item_adapter(d)

        Return a last item from the list.

        >>> a['a']
        3
    """
    return ItemAdapter(adaptee, -1)


class ItemAdapter(object):
    """ Adapts ``defaultdict(list)``.__getitem__ accessor to
        return item at ``index`` from the list. If ``key`` is not
        found return None.
    """
    __slots__ = ('adaptee', 'index')

    def __init__(self, adaptee, index):
        """ ``adaptee`` must be defaultdict(list).

            >>> d = defaultdict(list)
            >>> a = ItemAdapter(d, 0)

            Otherwise raise ``TypeError``.

            >>> ItemAdapter(None, 0) # doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            TypeError: ...
         """
        if adaptee is None or not isinstance(adaptee, dict):
            raise TypeError('first argument must be defaultdict(list)')
        self.adaptee = adaptee
        self.index = index

    def __getitem__(self, key):
        """
            >>> d = defaultdict(list)
            >>> d['a'].extend([1, 2, 3])
            >>> a = ItemAdapter(d, 0)

            Return a first item from the list.

            >>> a['a']
            1

            >>> a = ItemAdapter(d, -1)

            Return a last item from the list.

            >>> a['a']
            3

            If ``key`` not found return ``None``.

            >>> a['x']
        """
        l = self.adaptee[key]
        if l:
            return l[self.index]
        return None

    def get(self, key, default=None):
        """ Return the value for key if key is in the adaptee,
            else default. If default is not given, it defaults
            to None, so that this method never raises a KeyError.

            >>> d = defaultdict(list)
            >>> d['a'].extend([1, 2, 3])
            >>> a = ItemAdapter(d, 0)
            >>> a.get('a')
            1
            >>> a.get('b', 100)
            100
        """
        if key in self.adaptee:
            l = self.adaptee[key]
            if l:
                return l[self.index]
        return default


class attrdict(dict):
    """ A dictionary with attribute-style access. Maps attribute
        access to dictionary.

        >>> d = attrdict(a=1, b=2)
        >>> sorted(d.items())
        [('a', 1), ('b', 2)]
        >>> d.a
        1

        >>> d.c = 3
        >>> d.c
        3
        >>> d.d # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        AttributeError: ...
    """
    __slots__ = ()

    def __setattr__(self, key, value):
        return super(attrdict, self).__setitem__(key, value)

    def __getattr__(self, name):
        try:
            return super(attrdict, self).__getitem__(name)
        except KeyError:
            raise AttributeError(name)


class defaultattrdict(defaultdict):
    """ A dictionary with attribute-style access. Maps attribute
        access to dictionary.

        >>> d = defaultattrdict(str, a=1, b=2)
        >>> d.a
        1

        >>> d.c = 3
        >>> d.c
        3
        >>> d.d
        ''
    """
    __slots__ = ()

    def __setattr__(self, key, value):
        return super(defaultattrdict, self).__setitem__(key, value)

    def __getattr__(self, name):
        return super(defaultattrdict, self).__getitem__(name)


def distinct(seq):
    """ Returns generator for unique items in ``seq`` with preserved
        order.

        >>> list(distinct('1234512345'))
        ['1', '2', '3', '4', '5']

        If the order is not important consider using ``set`` which is
        approximately eight times faster on large sequences.

        >>> sorted(list(set('1234512345')))
        ['1', '2', '3', '4', '5']
    """
    unique = {}
    for item in seq:
        if item not in unique:
            unique[item] = None
            yield item


def gzip_iterator(items, compress_level=6):
    """ Iterates over ``items`` and returns generator of gzipped items.

        ``items`` - a list of bytes

        >>> items = [ntob('Hello World', 'latin1')]
        >>> result = list(gzip_iterator(items))
        >>> assert 3 == len(result)
        >>> assert GZIP_HEADER == result[0]
    """
    size = 0
    crc = 0
    gzip = zlib.compressobj(
        compress_level, zlib.DEFLATED, -zlib.MAX_WBITS,
        zlib.DEF_MEM_LEVEL, 0)
    yield GZIP_HEADER
    for item in items:
        size += len(item)
        crc = zlib.crc32(item, crc) & MAX_INT
        chunk = gzip.compress(item)
        if chunk:  # pragma: nocover
            yield chunk
    yield gzip.flush()
    yield struct.pack('<2L', crc, size & MAX_INT)
