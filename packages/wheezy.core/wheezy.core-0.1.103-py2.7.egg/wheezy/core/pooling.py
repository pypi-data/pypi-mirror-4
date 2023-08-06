
""" ``pooling`` module.
"""

from wheezy.core.comp import LifoQueue
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


class LazyPool(object):
    """ Lazy pool implementation.

        Allocates pool items as necessary.
    """

    def __init__(self, create_factory, size):
        """
            `create_factory` is a callable with an `item` as argument,
            this allows control `item` status before returning.
        """
        self.size = size
        items = LifoQueue(size)
        for i in xrange(size):
            items.put(None)
        self.__items = items
        self.get_back = items.put
        self.create_factory = create_factory

    def acquire(self):
        """ Return an item from pool. Blocks until an item
            is available.
        """
        return self.create_factory(self.__items.get())

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
