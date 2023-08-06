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
"""Test Support"""
import logging

try:
    # Python 2 BBB
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


def setUpLogging(logger, level=logging.DEBUG):
    buf = StringIO()
    handler = logging.StreamHandler(buf)
    handler._added_by_tests_ = True
    handler._old_propagate_ = logger.propagate
    handler._old_level_ = logger.level
    logger.propagate = False
    logger.addHandler(handler)
    logger.setLevel(level)
    return buf


def tearDownLogging(logger):
    for handler in logger.handlers:
        if hasattr(handler, '_added_by_tests_'):
            logger.removeHandler(handler)
            logger.propagate = handler._old_propagate_
            logger.setLevel(handler._old_level_)
            break

