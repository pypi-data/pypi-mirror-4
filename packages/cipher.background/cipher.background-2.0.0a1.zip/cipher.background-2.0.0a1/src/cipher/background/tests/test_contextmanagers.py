##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import doctest

import transaction
from zope.component import hooks
from zope.security.management import endInteraction, queryInteraction

from cipher.background import contextmanagers


class ConnectionStub(object):
    def __init__(self, db, verbose=False):
        self._db = db
        self._db.opened += 1
        self._verbose = verbose
        if self._verbose:
            print('Connection opened')
    def close(self):
        self._db.closed += 1
        if self._verbose:
            print('Connection closed')
    def __repr__(self):
        return '<ConnectionStub>'

class DbStub(object):
    opened = closed = 0
    def __init__(self, verbose=False):
        self._verbose = verbose
        self._objects = {}
    def open(self):
        return ConnectionStub(self, verbose=self._verbose)

class SiteStub(object):
    def __init__(self, name=''):
        self._p_jar = ConnectionStub(DbStub())
        self._p_oid = 42
        self._p_jar._db._objects[self._p_oid] = self
        self._name = name
    def getSiteManager(self):
        return None
    def __repr__(self):
        return 'SiteStub(%s)' % repr(self._name)

class DataManagerStub(object):
    def __init__(self):
        self.log = []
    def abort(self, t):
        print('aborted')
        self.log.append('aborted')
    def tpc_begin(self, t):
        pass
    def commit(self, t):
        print('committed')
        self.log.append('committed')
    def tpc_vote(self, t):
        pass
    def tpc_finish(self, t):
        pass


def doctest_ZopeInteraction():
    """Test for ZopeInteraction

        >>> print(queryInteraction())
        None

        >>> with contextmanagers.ZopeInteraction():
        ...     print(queryInteraction().__class__.__name__)
        ParanoidSecurityPolicy

        >>> print(queryInteraction())
        None

    """


def doctest_ZodbConnection():
    """Test the ZodbConnection context manager.

        >>> with contextmanagers.ZodbConnection(DbStub(verbose=True)) as conn:
        ...     print(conn)
        Connection opened
        <ConnectionStub>
        Connection closed

    """


def doctest_ZodbConnection_handles_exceptions():
    """Test the ZodbConnection context manager.

        >>> db = DbStub()
        >>> with contextmanagers.ZodbConnection(db) as conn:
        ...     raise Exception()
        Traceback (most recent call last):
          ...
        Exception

        >>> (db.opened, db.closed)
        (1, 1)

    """


def doctest_ZopeSite():
    """Test the ZopeSite context manager.

    Initially there's no site

        >>> print(hooks.getSite())
        None

    It is set inside the context manager

        >>> site = SiteStub()
        >>> with contextmanagers.ZopeSite(site) as s:
        ...     print(hooks.getSite() is site)
        ...     print(s is site)
        True
        True

    and cleared when you're done

        >>> print(hooks.getSite())
        None

    """


def doctest_ZopeSite_can_be_nested():
    """Test the ZopeSite context manager.

    ZopeSite() can be nested

        >>> with contextmanagers.ZopeSite(SiteStub('outer')):
        ...     print(hooks.getSite())
        ...     with contextmanagers.ZopeSite(SiteStub('inner')):
        ...         print(hooks.getSite())
        ...     print(hooks.getSite())
        SiteStub('outer')
        SiteStub('inner')
        SiteStub('outer')

    """


def doctest_ZopeSite_handles_exceptions():
    """Test the ZopeSite context manager.

    If an exception happens, the site is reset

        >>> site = SiteStub()
        >>> with contextmanagers.ZopeSite(site):
        ...     raise Exception()
        Traceback (most recent call last):
          ...
        Exception

        >>> print(hooks.getSite())
        None

    """


def doctest_ZopeTransaction():
    """Test the ZopeTransaction context manager.

        >>> with contextmanagers.ZopeTransaction() as t:
        ...     print(t is transaction.get())
        True

    """


def doctest_ZopeTransaction_with_user():
    """Test the ZopeTransaction context manager.

        >>> with contextmanagers.ZopeTransaction(user='admin') as t:
        ...     print(repr(t.user))
        '/ admin'

    """


def doctest_ZopeTransaction_with_note():
    """Test the ZopeTransaction context manager.

        >>> with contextmanagers.ZopeTransaction(note='doing stuff') as t:
        ...     print(repr(t.description))
        'doing stuff'

    """


def doctest_ZopeTransaction_with_path():
    """Test the ZopeTransaction context manager.

        >>> with contextmanagers.ZopeTransaction(user='bob', path='/url') as t:
        ...     print(repr(t.user))
        '/url bob'

    """


def doctest_ZopeTransaction_commits_on_success():
    """Test the ZopeTransaction context manager.

        >>> with contextmanagers.ZopeTransaction() as t:
        ...     t.join(DataManagerStub())
        ...     print('okay, time to commit')
        okay, time to commit
        committed

    """


def doctest_ZopeTransaction_aborts_on_failure():
    """Test the ZopeTransaction context manager.

        >>> dm = DataManagerStub()
        >>> with contextmanagers.ZopeTransaction() as t:
        ...     t.join(dm)
        ...     raise Exception
        Traceback (most recent call last):
          ...
        Exception

        >>> dm.log
        ['aborted']

    """


def doctest_ZopeTransaction_starts_new_transaction():
    """Test the ZopeTransaction context manager.

        >>> transaction.get().join(DataManagerStub())
        >>> with contextmanagers.ZopeTransaction() as t:
        ...     print('inside new transaction')
        aborted
        inside new transaction

    XXX: this is surprising, and therefore bad design.  Consider changing
    ZopeTransaction() to assert that transaction.get()._resources == [],
    so that the old transaction is not quietly dropped.
    """


def setUp(test):
    pass


def tearDown(test):
    endInteraction()
    hooks.setSite(None)
    transaction.abort()


def test_suite():
    return doctest.DocTestSuite(setUp=setUp, tearDown=tearDown)
