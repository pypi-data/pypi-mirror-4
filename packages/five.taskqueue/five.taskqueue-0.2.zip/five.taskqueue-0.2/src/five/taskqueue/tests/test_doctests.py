##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Remote Task test setup

"""
__docformat__ = "reStructuredText"

from Testing import ZopeTestCase

from zope.testing.doctest import INTERPRET_FOOTNOTES
from zope.testing.loggingsupport import InstalledHandler
import doctest
import random
import unittest
import logging

from five.taskqueue import service

ZopeTestCase.installProduct('Five')


def _configure_conflict_error_log_level():
    import App.config
    config = App.config.getConfiguration()
    config.conflict_error_log_level = logging.INFO
    App.config.setConfiguration(config)


def setUp(test):
    test.globs['root'] = ZopeTestCase.base.app()
    # As task will be run in different threads, we cannot rely on print
    # results. We need to log calls to prove correctness.
    log_info = InstalledHandler('z3c.taskqueue')
    test.globs['log_info'] = log_info
    # We pass the ZPublisher conflict logger to prove that no conflict
    # happened.
    conflict_logger = InstalledHandler('ZPublisher.Conflict')
    test.globs['conflict_logger'] = conflict_logger
    # Make sure ZPublisher conflict error log level is setup.
    _configure_conflict_error_log_level()
    test.origArgs = service.TaskService.processorArguments
    service.TaskService.processorArguments = {'waitTime': 0.0}
    # Make tests predictable
    random.seed(27)


def tearDown(test):
    random.seed()
    service.TaskService.processorArguments = test.origArgs


class TestIdGenerator(unittest.TestCase):

    def setUp(self):
        random.seed(27)
        self.service = service.TaskService()

    def tearDown(self):
        random.seed()

    def test_sequence(self):
        id = 1392637175
        self.assertEquals(id, self.service._generateId())
        self.assertEquals(id + 1, self.service._generateId())
        self.assertEquals(id + 2, self.service._generateId())
        self.assertEquals(id + 3, self.service._generateId())

    def test_in_use_randomises(self):
        id = 1392637175
        self.assertEquals(id, self.service._generateId())
        self.service.jobs[id + 1] = object()
        id = 1506179619
        self.assertEquals(id, self.service._generateId())
        self.assertEquals(id + 1, self.service._generateId())
        self.service.jobs[id + 1] = object()
        self.assertEquals(id + 2, self.service._generateId())


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestIdGenerator),
        ZopeTestCase.ZopeDocFileSuite('processor.txt',
                     package='five.taskqueue.tests',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE
                     | doctest.ELLIPSIS
                     | INTERPRET_FOOTNOTES),
        ))
