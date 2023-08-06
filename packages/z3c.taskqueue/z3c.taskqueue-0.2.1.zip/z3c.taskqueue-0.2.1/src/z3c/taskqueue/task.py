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
"""Task Service Implementation

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.interface

from zope.schema.fieldproperty import FieldProperty

from z3c.taskqueue import interfaces


class TaskError(Exception):
    """An error occurred while executing the task."""
    pass


class SimpleTask(object):
    """A simple, non-persistent task implementation."""
    zope.interface.implements(interfaces.ITask)

    inputSchema = FieldProperty(interfaces.ITask['inputSchema'])
    outputSchema = FieldProperty(interfaces.ITask['outputSchema'])

    def __init__(self, func):
        self.func = func

    def __call__(self, service, jobid, input):
        return self.func(input)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.func)


class EchoTask(object):
    zope.interface.implements(interfaces.ITask)

    def __call__(self, service, input):
        return input

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__)
