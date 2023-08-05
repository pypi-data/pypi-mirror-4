
""" ``pooling`` module.
"""

from wheezy.core.comp import Queue
from wheezy.core.comp import xrange


class EagerPool(object):
    """ Eager pool implementation.

        Allocates all pool items during initialization.
    """

    def __init__(self, create_factory, size):
        self.size = size
        items = Queue(size)
        for i in xrange(size):
            items.put(create_factory())
        self.__items = items
        self.acquire = items.get
        self.get_back = items.put

    @property
    def count(self):
        """ Returns a number of available items in the pool.
        """
        return self.__items.qsize()


class Pooled(object):
    """ ``Pooled`` serves context manager purpose, effectively acquiring and
        returning item to the pool.

        Here is an example::

            with Pooled(pool) as item:
                # do something with item
    """
    __slots__ = ('pool', 'item')

    def __init__(self, pool):
        self.pool = pool

    def __enter__(self):
        self.item = item = self.pool.acquire()
        return item

    def __exit__(self, exc_type, exc_value, traceback):
        self.pool.get_back(self.item)
        self.item = None
