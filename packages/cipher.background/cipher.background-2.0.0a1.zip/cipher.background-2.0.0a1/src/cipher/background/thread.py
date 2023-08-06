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
import threading
import logging

from .contextmanagers import (ZopeInteraction, ZodbConnection, ZopeSite,
                              ZopeTransaction)


log = logging.getLogger(__name__)


class BackgroundWorkerThread(threading.Thread):
    """A background thread that can access the ZODB and a local site.

    Abstracts the plumbing away so we can focus on the important details.

    Subclasses ought to override the following methods:

      - scheduleNextWork -- sleep until the next job becomes available,
        or return False if the thread should terminate

      - doWork -- perform whatever work is necessary

      - doCleanup -- perform whatever cleanup is necessary, called even
        when doWork() raises an exception.

    """

    # Feel free to replace these with more descriptive notes in subclasses
    description = "background worker thread (%(class_name)s) for %(site_name)s"
    work_transaction_note = "%(thread_name)s"
    cleanup_transaction_note = "%(thread_name)s cleanup"

    log = log  # let subclasses use a different logger if they want

    def __init__(self, site_db, site_oid, site_name, user_name, daemon=True):
        """Create a thread."""
        self.site_db = site_db
        self.site_oid = site_oid
        self.site_name = site_name
        self.user_name = user_name
        super(BackgroundWorkerThread, self).__init__(
            name=self.description % dict(class_name=self.__class__.__name__,
                                         site_name=self.site_name,
                                         user_name=self.user_name),
        )
        if daemon:
            self.setDaemon(True)

    @classmethod
    def forSite(cls, site, user_name, daemon=True):
        """Create a thread."""
        return cls(site._p_jar.db(), site._p_oid, site.__name__, user_name,
                   daemon=daemon)

    def getTransactionNote(self):
        """Note for the ZODB transaction record.

        Visible in tools like @@zodbbrowser.
        """
        return self.work_transaction_note % dict(
                    thread_name=self.name,
                    class_name=self.__class__.__name__,
                    site_name=self.site_name,
                    user_name=self.user_name)

    def getCleanupNote(self):
        """Note for the ZODB transaction record for the cleanup transaction.

        Visible in tools like @@zodbbrowser.
        """
        return self.cleanup_transaction_note % dict(
                    thread_name=self.name,
                    class_name=self.__class__.__name__,
                    site_name=self.site_name,
                    user_name=self.user_name)

    def getSite(self, connection):
        return connection.get(self.site_oid)

    def run(self):
        """Main loop of the thread."""
        try:
            while self.scheduleNextWork():
                with ZopeInteraction():
                    with ZodbConnection(self.site_db) as conn:
                        try:
                            with ZopeSite(self.getSite(conn)):
                                try:
                                    with ZopeTransaction(
                                            user=self.user_name,
                                            note=self.getTransactionNote()):
                                        self.doWork()
                                finally:
                                    # Do the cleanup in a new transaction, as
                                    # the current one may be doomed or
                                    # something.  Also do it while the site
                                    # is available, since we may need to access
                                    # local utilities during the cleanup
                                    with ZopeTransaction(
                                            user=self.user_name,
                                            note=self.getCleanupNote()):
                                        self.doCleanup()
                        except:
                            # Note: log the exception while the ZODB connection
                            # is still open; we may need it for repr() of
                            # objects in various __traceback_info__s.
                            self.log.exception("Exception in %s" % self.name)
        except:
            self.log.exception("Exception in %s, thread terminated" % self.name)

    def scheduleNextWork(self):
        """Sleep until some work is available.

        Return True if there is work, and False if the thread should terminate
        now.

        Override it, otherwise there's no point!
        """
        return False

    def doWork(self):
        """Perform the work.

        Does nothing by default.  Override it, otherwise there's no point!

        This method is called with a local site set and a working ZODB
        connection.
        """

    def doCleanup(self):
        """Clean up if necessary.

        Does nothing by default.  Override if you need to do some sort of
        cleanup.

        Cleanup is also called when doWork() raises an exception.  It is
        performed in a separate transaction.  It can access the site.
        """
