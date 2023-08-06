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
from __future__ import print_function
import doctest

import transaction
from zope.component.hooks import getSite, setSite
from zope.security.management import queryInteraction, endInteraction

from cipher.background import testing
from cipher.background.thread import BackgroundWorkerThread, log


class SiteStub(object):
    __name__ = 'testsite'
    def __init__(self):
        self._p_jar = ConnectionStub(DbStub())
        self._p_oid = 42
        self._p_jar._db._objects[self._p_oid] = self
        self.patients = {}
    def getSiteManager(self):
        return None

class ConnectionStub(object):
    def __init__(self, db, verbose=False):
        self._db = db
        self._db.opened += 1
        self._verbose = verbose
    def db(self):
        return self._db
    def get(self, oid):
        return self._db._objects[oid]
    def close(self):
        self._db.closed += 1

class DbStub(object):
    opened = closed = 0
    def __init__(self, verbose=False):
        self._verbose = verbose
        self._objects = {}
    def open(self):
        return ConnectionStub(self, verbose=self._verbose)


class BackgroundWorkerThreadForTest(BackgroundWorkerThread):

    def __init__(self, *args, **kw):
        super(BackgroundWorkerThreadForTest, self).__init__(*args, **kw)
        self._tasks = [None] * 5

    def scheduleNextWork(self):
        if not self._tasks:
            log.info('no tasks left to schedule')
            return False
        log.info('scheduling a task')
        self._tasks.pop()
        return True


def doctest_BackgroundWorkerThread():
    """Test for BackgroundWorkerThread.__init__

        >>> site = SiteStub()
        >>> thread = BackgroundWorkerThreadForTest(
        ...     site_db=site._p_jar.db(), site_oid=site._p_oid,
        ...     site_name='testsite', user_name='someuser',
        ... )
        >>> thread.name
        'background worker thread (BackgroundWorkerThreadForTest) for testsite'

    """


def doctest_BackgroundWorkerThread_forSite():
    """Test for BackgroundWorkerThread.forSite

        >>> site = SiteStub()
        >>> thread = BackgroundWorkerThreadForTest.forSite(
        ...     site=site,
        ...     user_name='someuser',
        ... )
        >>> thread.name
        'background worker thread (BackgroundWorkerThreadForTest) for testsite'

    """


def doctest_BackgroundWorkerThread_getTransactionNote():
    """Test for BackgroundWorkerThread.getTransactionNote

        >>> site = SiteStub()
        >>> thread = BackgroundWorkerThreadForTest.forSite(site, 'someuser')
        >>> thread.name = 'my thread'

    Default transaction note is just the thread name

        >>> thread.getTransactionNote()
        'my thread'

    You can customize it by changing the work_transaction_note attribute

        >>> thread.work_transaction_note = ('work for %(site_name)s'
        ...                                 ' on behalf of %(user_name)s')
        >>> thread.getTransactionNote()
        'work for testsite on behalf of someuser'

    """


def doctest_BackgroundWorkerThread_getCleanupNote():
    """Test for BackgroundWorkerThread.getCleanupNote

        >>> site = SiteStub()
        >>> thread = BackgroundWorkerThreadForTest.forSite(site, 'someuser')
        >>> thread.name = 'my thread'

    Default transaction note is just the thread name with " cleanup" tacked on

        >>> thread.getCleanupNote()
        'my thread cleanup'

    You can customize it by changing the cleanup_transaction_note attribute

        >>> thread.cleanup_transaction_note = ('cleanup for %(site_name)s'
        ...                                    ' on behalf of %(user_name)s')
        >>> thread.getCleanupNote()
        'cleanup for testsite on behalf of someuser'

    """


def doctest_BackgroundWorkerThread_run():
    """Test for BackgroundWorkerThread.run

        >>> site = SiteStub()
        >>> thread = BackgroundWorkerThreadForTest.forSite(site, 'someuser')

        >>> logbuf = testing.setUpLogging(log)

    The method gives us a Zope interaction, a ZODB connection (not directly
    available), and a site (loaded from the DB connection).

        >>> def doWork(self):
        ...     log.info('got interaction: %s', queryInteraction() is not None)
        ...     log.info('got site: %s', getSite() is not None)
        ...     self._tasks = [] # terminate early
        >>> thread.doWork = doWork.__get__(thread)

        >>> thread.run()

        >>> print(logbuf.getvalue().strip()) # doctest: +ELLIPSIS
        scheduling a task
        got interaction: True
        got site: True
        no tasks left to schedule

        >>> testing.tearDownLogging(log)

    We can check that the database connection was closed

        >>> site._p_jar.db().opened
        2
        >>> site._p_jar.db().closed
        1

    The site was reset and the interaction ended

        >>> queryInteraction()
        >>> getSite()

    """


def doctest_BackgroundWorkerThread_run_exception_handling():
    """Test for BackgroundWorkerThread.run

        >>> site = SiteStub()
        >>> thread = BackgroundWorkerThreadForTest.forSite(site, 'someuser')
        >>> thread.name = 'this thread'

        >>> logbuf = testing.setUpLogging(log)

    What if an exception happens during the background processing?

        >>> def doWork(self):
        ...     self._tasks = []
        ...     raise Exception('something happened')
        >>> thread.doWork = doWork.__get__(thread)

        >>> thread.run()

    The exception is mentioned in the log

        >>> print(logbuf.getvalue().strip()) # doctest: +ELLIPSIS
        scheduling a task
        Exception in this thread
        Traceback (most recent call last):
          ...
        Exception: something happened
        no tasks left to schedule

        >>> testing.tearDownLogging(log)

    We can check that the database connection was closed

        >>> site._p_jar.db().opened
        2
        >>> site._p_jar.db().closed
        1

    The site was reset and the interaction ended

        >>> queryInteraction()
        >>> getSite()

    """


def doctest_BackgroundWorkerThread_run_outer_exception_handling():
    """Test for BackgroundWorkerThread.run

        >>> site = SiteStub()
        >>> thread = BackgroundWorkerThreadForTest.forSite(site, 'someuser')
        >>> thread.name = 'this thread'

        >>> logbuf = testing.setUpLogging(log)

    What if an exception happens during the scheduling?

        >>> def scheduleNextWork(self):
        ...     log.info('scheduling a task')
        ...     raise Exception('something happened')
        >>> thread.scheduleNextWork = scheduleNextWork.__get__(thread)

        >>> thread.run()

    The exception is mentioned in the log and the thread is terminated

        >>> print(logbuf.getvalue().strip()) # doctest: +ELLIPSIS
        scheduling a task
        Exception in this thread, thread terminated
        Traceback (most recent call last):
          ...
        Exception: something happened

        >>> testing.tearDownLogging(log)

    """


def doctest_BackgroundWorkerThread_scheduleNextWork():
    """Test for BackgroundWorkerThread.scheduleNextWork

        >>> site = SiteStub()
        >>> thread = BackgroundWorkerThread.forSite(site, 'someuser')

    The default implementation terminates the thread at once.

        >>> thread.scheduleNextWork()
        False

    """


def setUp(test):
    pass


def tearDown(test):
    testing.tearDownLogging(log)
    setSite(None)
    endInteraction()
    transaction.abort()


def test_suite():
    return doctest.DocTestSuite(setUp=setUp, tearDown=tearDown)
