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
"""Helpful context managers for Zope 3."""

from __future__ import absolute_import
from contextlib import contextmanager, closing

import transaction
from zope.component import hooks
from zope.security.management import newInteraction, endInteraction


@contextmanager
def ZopeInteraction(*participations):
    """Perform work within an interaction.

    Raises an error if the calling thread already has an interaction.

    Example::

        with ZopeInteraction():
            doStuff()

    """
    newInteraction(*participations)
    try:
        yield None
    finally:
        endInteraction()


@contextmanager
def ZodbConnection(db):
    """Perform work with a ZODB connection.

    Example::

        with ZodbConnection(DB(FileStorage('Data.fs'))) as conn:
            doStuff(conn.root())

    """
    with closing(db.open()) as conn:
        yield conn


@contextmanager
def ZopeSite(site):
    """Perform work with a local Zope site.

    Example::

        with ZopeSite(site) as site:
            doStuff()

    """
    oldsite = hooks.getSite()
    try:
        hooks.setSite(site)
        yield site
    finally:
        hooks.setSite(oldsite)


@contextmanager
def ZopeTransaction(user=None, note=None, path="/"):
    """Perform work within a new fresh transaction.

    Commits on success, aborts on exception.

    Example::

        with ZopeTransaction(user='root', note='system maintenance') as txn:
            txn.setExtendedInfo('foo', 'bar')
            doStuff()

    WARNING: the "new fresh transaction" in the description above means that
    any previous but not yet committed transaction will be aborted!
    """
    # XXX Note that transaction.begin() acts the same as transaction.abort(),
    # i.e.  discards the previous transaction.  This is desired in some
    # circumstances but surprising and painful in others.  I think it'd be nice
    # to have an explicit assertion verifying that the current transaction is
    # empty -- let the users call transaction.abort() explicitly if they want
    # that.
    txn = transaction.begin()
    try:
        if user:
            txn.setUser(user, path)
        if note:
            txn.note(note)
        yield txn
        # don't use txn -- it may have already been committed or aborted,
        # and a new transaction started
        transaction.commit()
    except:
        transaction.abort()
        raise

