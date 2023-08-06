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

from z3c.taskqueue import service
from zope.testing.doctest import INTERPRET_FOOTNOTES
from zope.testing.doctestunit import DocFileSuite
from zope.testing.loggingsupport import InstalledHandler
from zope.app.testing.setup import (placefulSetUp, placefulTearDown)
import doctest
import random
import unittest


def setUp(test):
    root = placefulSetUp(site=True)
    test.globs['root'] = root
    log_info = InstalledHandler('z3c.taskqueue')
    test.globs['log_info'] = log_info
    test.origArgs = service.TaskService.processorArguments
    service.TaskService.processorArguments = {'waitTime': 0.0}
    # Make tests predictable
    random.seed(27)


def tearDown(test):
    placefulTearDown()
    random.seed()
    service.TaskService.processorArguments = test.origArgs


class TestIdGenerator(unittest.TestCase):

    def setUp(self):
        random.seed(27)
        self.service = service.TaskService()

    def tearDown(self):
        random.seed()

    def test_sequence(self):
        self.assertEquals(1392637175, self.service._generateId())
        self.assertEquals(1392637176, self.service._generateId())
        self.assertEquals(1392637177, self.service._generateId())
        self.assertEquals(1392637178, self.service._generateId())

    def test_in_use_randomises(self):
        self.assertEquals(1392637175, self.service._generateId())
        self.service.jobs[1392637176] = object()
        self.assertEquals(1506179619, self.service._generateId())
        self.assertEquals(1506179620, self.service._generateId())
        self.service.jobs[1506179621] = object()
        self.assertEquals(2055242787, self.service._generateId())


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestIdGenerator),
        DocFileSuite('README.txt',
                     'startlater.txt',
                     'processor.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE
                     | doctest.ELLIPSIS
                     | INTERPRET_FOOTNOTES),
        ))
