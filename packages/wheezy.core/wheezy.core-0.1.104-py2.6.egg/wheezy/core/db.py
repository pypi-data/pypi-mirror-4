
""" ``session`` module.
"""

import warnings

from wheezy.core.introspection import import_name
from wheezy.core.uuid import shrink_uuid

uuid4 = import_name('uuid.uuid4')

SESSION_STATUS_IDLE = 0
SESSION_STATUS_ENTERED = 1
SESSION_STATUS_ACTIVE = 2


class Session(object):
    """ Session works with a pool of database connections.
        Database connection must be implemented per Database API
        Specification v2.0
        (see `PEP0249 <http://www.python.org/dev/peps/pep-0249/>`_).
    """

    __slots__ = ('pool', 'status', '__connection')

    def __init__(self, pool):
        """ Initialize a new instance of database session.

            The *pool* argument is an object that implement pooling
            interface (acquire/get_back).
        """
        self.pool = pool
        self.status = SESSION_STATUS_IDLE
        self.__connection = None

    def __enter__(self):
        assert self.status == SESSION_STATUS_IDLE
        self.status = SESSION_STATUS_ENTERED
        return self

    @property
    def connection(self):
        """ Return the session connection. Not intended to be used
            directly, use `cursor` method instead.
        """
        if self.__connection:
            return self.__connection
        assert self.status == SESSION_STATUS_ENTERED
        self.__connection = connection = self.pool.acquire()
        self.status = SESSION_STATUS_ACTIVE
        self.on_active(connection)
        return connection

    def on_active(self, connection):
        pass

    def cursor(self, *args, **kwargs):
        """ Return a new cursor object using the session connection.
        """
        return self.connection.cursor(*args, **kwargs)

    def commit(self):
        """ Commit any pending transaction to the database.
        """
        assert self.status != SESSION_STATUS_IDLE
        if self.status != SESSION_STATUS_ACTIVE:
            return
        self.status = SESSION_STATUS_ENTERED
        connection = self.__connection
        self.__connection = None
        try:
            connection.commit()
        finally:
            self.pool.get_back(connection)

    def __exit__(self, exc_type, exc_value, traceback):
        self.status = SESSION_STATUS_IDLE
        connection = self.__connection
        if connection:
            self.__connection = None
            try:
                connection.rollback()
            finally:
                self.pool.get_back(connection)


class TPCSession(object):
    """ Two-Phase Commit protocol session that works with a pool of
        database connections.
        Database connection must be implemented per Database API
        Specification v2.0
        (see `PEP0249 <http://www.python.org/dev/peps/pep-0249/>`_).
    """

    __slots__ = ('format_id', 'global_transaction_id', 'branch_qualifier',
                 'enlised_sessions', 'status')

    def __init__(self, format_id=7, global_transaction_id=None,
                 branch_qualifier=''):
        """ Initialize a new instance of Two-Phase Commit protocol database
        session.
        """
        self.format_id = format_id
        self.global_transaction_id = global_transaction_id
        self.branch_qualifier = branch_qualifier
        self.enlised_sessions = []
        self.status = SESSION_STATUS_IDLE

    def __enter__(self):
        assert self.status == SESSION_STATUS_IDLE
        assert not self.enlised_sessions
        self.status = SESSION_STATUS_ENTERED
        return self

    def enlist(self, session):
        """ Begins a TPC transaction with the given session.
        """
        assert session
        assert self.status != SESSION_STATUS_IDLE
        self.enlised_sessions.append(session)
        session.__enter__()
        c = session.connection
        xid = c.xid(self.format_id,
                    self.global_transaction_id or shrink_uuid(uuid4()),
                    self.branch_qualifier)
        c.tpc_begin(xid)
        self.status = SESSION_STATUS_ACTIVE

    def commit(self):
        """ Commit any pending transaction to the database.
        """
        assert self.status != SESSION_STATUS_IDLE
        if self.status != SESSION_STATUS_ACTIVE:
            return
        sessions = self.enlised_sessions
        connections = [s.connection for s in sessions
                       if s.status == SESSION_STATUS_ACTIVE]
        for c in connections:
            c.tpc_prepare()
        for c in connections:
            c.tpc_commit()
        for s in sessions:
            s.__exit__(None, None, None)
        self.enlised_sessions = []
        self.status = SESSION_STATUS_ENTERED

    def __exit__(self, exc_type, exc_value, traceback):
        sessions = self.enlised_sessions
        self.status = SESSION_STATUS_IDLE
        self.enlised_sessions = []
        for s in sessions:
            if s.status == SESSION_STATUS_ACTIVE:
                try:
                    s.connection.tpc_rollback()
                except Exception:
                    warnings.warn('An error occured while rolling back '
                                  'two phase transaction.')
            s.__exit__(exc_type, exc_value, traceback)


class NullSession(object):
    """ Null session is supposed to be used in mock scenarios.
    """

    def __init__(self):
        self.status = SESSION_STATUS_IDLE

    def __enter__(self):
        assert self.status == SESSION_STATUS_IDLE
        self.status = SESSION_STATUS_ENTERED
        return self

    @property
    def connection(self):
        raise AssertionError('Not intended to be used directly. '
                             'Use cursor() method instead.')

    def cursor(self, *args, **kwargs):
        """ Ensure session is entered.
        """
        assert self.status == SESSION_STATUS_ENTERED

    def commit(self):
        """ Simulates commit. Asserts the session is used in scope.
        """
        assert self.status != SESSION_STATUS_IDLE
        self.status = SESSION_STATUS_ENTERED

    def __exit__(self, exc_type, exc_value, traceback):
        assert self.status == SESSION_STATUS_ENTERED
        self.status = SESSION_STATUS_IDLE


class NullTPCSession(object):
    """ Null TPC session is supposed to be used in mock scenarios.
    """

    def __init__(self):
        self.status = SESSION_STATUS_IDLE

    def __enter__(self):
        assert self.status == SESSION_STATUS_IDLE
        self.status = SESSION_STATUS_ENTERED
        return self

    def enlist(self, session):
        """ Ensure session is entered.
        """
        assert session
        assert self.status != SESSION_STATUS_IDLE
        self.status = SESSION_STATUS_ACTIVE

    def commit(self):
        """ Simulates commit. Asserts the session is used in scope.
        """
        assert self.status != SESSION_STATUS_IDLE
        self.status = SESSION_STATUS_ENTERED

    def __exit__(self, exc_type, exc_value, traceback):
        assert self.status != SESSION_STATUS_IDLE
        self.status = SESSION_STATUS_IDLE
