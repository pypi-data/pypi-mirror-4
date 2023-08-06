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
"""Task Service testing tools

$Id$
"""
__docformat__ = "reStructuredText"

import datetime
import zc.queue
import zope.component
import zope.interface
from BTrees.IOBTree import IOBTree
from zope.app.container import contained
from z3c.taskqueue import interfaces, job, task


class ExceptionTask(object):
    """Task to test exception handling"""
    zope.interface.implements(interfaces.ITask)

    def __call__(self, service, id, input):
        # always raise division by zero
        1 / 0

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__)


###############################################################################
#
# Stub implementations (Note: use the ITaskStub interface for this service)
#
###############################################################################


class QueueStub(object):

    zope.interface.implements(zc.queue.interfaces.IQueue)

    def __init__(self):
        self._data = ()

    def pull(self, index=0):
        if index < 0:
            len_self = len(self._data)
            index += len_self
            if index < 0:
                raise IndexError(index - len_self)
        res = self._data[index]
        self._data = self._data[:index] + self._data[index + 1:]
        return res

    def put(self, item):
        self._data += (item,)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, index):
        return self._data[index] # works with passing a slice too

    def __nonzero__(self):
        return bool(self._data)


class ITaskStub(interfaces.ITask):
    """Task stub interface for stub tasks."""


class TaskServiceStub(contained.Contained):
    """A task service stub.

    The available tasks for this service are managed as stub utilities.
    This task service stub could be helpful if you need to use a different
    testing setup. If so, register your own testing ITaskStub in ftesting.zcml.
    """
    zope.interface.implements(interfaces.ITaskService)

    # NOTE: we use ITaskStub instead of ITask
    taskInterface = ITaskStub

    def __init__(self):
        super(TaskServiceStub, self).__init__()
        self._counter = 1
        self.jobs = IOBTree()
        self._queue = QueueStub()

    def getAvailableTasks(self):
        """See interfaces.ITaskService"""
        return dict(zope.component.getUtilitiesFor(self.taskInterface))

    def add(self, task, input=None, startLater=False, jobClass=None):
        """See interfaces.ITaskService"""
        if task not in self.getAvailableTasks():
            raise ValueError('Task does not exist')
        if jobClass == None:
            jobClass = job.Job
        jobid = self._counter
        self._counter += 1
        newjob = jobClass(jobid, task, input)
        self.jobs[jobid] = newjob
        if startLater:
            newjob.status = interfaces.STARTLATER
        else:
            self._queue.put(newjob)
            newjob.status = interfaces.QUEUED
        return jobid

    def startJob(self, jobid):
        job = self.jobs[jobid]
        if job.status == interfaces.STARTLATER:
            self._queue.put(job)
            job.status = interfaces.QUEUED
            return True
        return False

    def cancel(self, jobid):
        """See interfaces.ITaskService"""
        for idx, job in enumerate(self._queue):
            if job.id == jobid:
                job.status = interfaces.CANCELLED
                self._queue.pull(idx)
                break

    def getStatus(self, jobid):
        """See interfaces.ITaskService"""
        return self.jobs[jobid].status

    def getResult(self, jobid):
        """See interfaces.ITaskService"""
        return self.jobs[jobid].output

    def getError(self, jobid):
        """See interfaces.ITaskService"""
        return str(self.jobs[jobid].error)

    def processNext(self):
        job = self._queue.pull()
        jobtask = zope.component.getUtility(
            self.taskInterface, name=job.task)
        job.started = datetime.datetime.now()
        try:
            job.output = jobtask(self, job.id, job.input)
            job.status = interfaces.COMPLETED
        except task.TaskError, error:
            job.error = error
            job.status = interfaces.ERROR
        job.completed = datetime.datetime.now()
