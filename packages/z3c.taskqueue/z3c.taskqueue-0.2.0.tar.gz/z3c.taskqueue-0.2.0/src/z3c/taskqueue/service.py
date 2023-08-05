##############################################################################
#
# Copyright (c) 2006, 2007 Zope Foundation and Contributors.
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

"""
__docformat__ = 'restructuredtext'

from zope.traversing.api import getParents

from BTrees import family32

from z3c.taskqueue.baseservice import BaseTaskService


class TaskService(BaseTaskService):
    containerClass = family32.IO.BTree
    maxint = family32.maxint

    def getServicePath(self):
        path = [parent.__name__ for parent in getParents(self)
                       if parent.__name__]
        path.reverse()
        path.append(self.__name__)
        return path
