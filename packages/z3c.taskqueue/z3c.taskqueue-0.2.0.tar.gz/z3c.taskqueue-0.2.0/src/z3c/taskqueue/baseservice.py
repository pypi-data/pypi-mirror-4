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

from zope import component
from zope.container import contained
from zope.component.interfaces import ComponentLookupError
import threading
import datetime
import logging
import persistent
import random
import time
import zc.queue
import zope.interface

from z3c.taskqueue import interfaces, job, task
from z3c.taskqueue import processor
import z3c.taskqueue

log = logging.getLogger('z3c.taskqueue')

storage = threading.local()


class BaseTaskService(contained.Contained, persistent.Persistent):
    """A persistent task service.

    The available tasks for this service are managed as utilities.
    """
    zope.interface.implements(interfaces.ITaskService)

    taskInterface = interfaces.ITask

    _v_nextid = None
    containerClass = None
    processorFactory = processor.SimpleProcessor
    processorArguments = {'waitTime': 1.0}

    def __init__(self):
        super(BaseTaskService, self).__init__()
        self.jobs = self.containerClass()
        self._scheduledJobs = self.containerClass()
        self._queue = zc.queue.Queue()
        self._scheduledQueue = zc.queue.Queue()

    def getAvailableTasks(self):
        """See interfaces.ITaskService"""
        return dict(component.getUtilitiesFor(self.taskInterface))

    def add(self, task, input=None, startLater=False):
        """See interfaces.ITaskService"""
        if task not in self.getAvailableTasks():
            raise ValueError('Task does not exist')
        jobid = self._generateId()
        newjob = job.Job(jobid, task, input)
        self.jobs[jobid] = newjob
        if startLater:
            newjob.status = interfaces.STARTLATER
        else:
            self._queue.put(newjob)
            newjob.status = interfaces.QUEUED
        return jobid

    def addCronJob(self, task, input=None,
                   minute=(),
                   hour=(),
                   dayOfMonth=(),
                   month=(),
                   dayOfWeek=(),
                   delay=None,
                  ):
        jobid = self._generateId()
        newjob = job.CronJob(jobid, task, input,
                minute, hour, dayOfMonth, month, dayOfWeek, delay)
        self.jobs[jobid] = newjob
        if newjob.delay is None:
            newjob.status = interfaces.CRONJOB
        else:
            newjob.status = interfaces.DELAYED
        self._scheduledQueue.put(newjob)
        return jobid

    def startJob(self, jobid):
        job = self.jobs[jobid]
        if job.status == interfaces.STARTLATER:
            self._queue.put(job)
            job.status = interfaces.QUEUED
            return True
        return False

    def reschedule(self, jobid):
        self._scheduledQueue.put(self.jobs[jobid])

    def clean(self, status=[interfaces.CANCELLED, interfaces.ERROR,
                            interfaces.COMPLETED]):
        """See interfaces.ITaskService"""
        allowed = [interfaces.CANCELLED, interfaces.ERROR,
                   interfaces.COMPLETED]
        for key in list(self.jobs.keys()):
            job = self.jobs[key]
            if job.status in status:
                if job.status not in allowed:
                    raise ValueError('Not allowed status for removing. %s' %
                        job.status)
                del self.jobs[key]

    def cancel(self, jobid):
        """See interfaces.ITaskService"""
        for idx, job in enumerate(self._queue):
            if job.id == jobid:
                job.status = interfaces.CANCELLED
                self._queue.pull(idx)
                break
        if jobid in self.jobs:
            job = self.jobs[jobid]
            if (job.status == interfaces.CRONJOB
                or job.status == interfaces.DELAYED
                or job.status == interfaces.STARTLATER):
                job.status = interfaces.CANCELLED

    def getStatus(self, jobid):
        """See interfaces.ITaskService"""
        return self.jobs[jobid].status

    def getResult(self, jobid):
        """See interfaces.ITaskService"""
        return self.jobs[jobid].output

    def getError(self, jobid):
        """See interfaces.ITaskService"""
        return str(self.jobs[jobid].error)

    def hasJobsWaiting(self, now=None):
        """
        are there jobs waiting ?
        """
        # If there is are any simple jobs in the queue, we have work to do.
        if self._queue:
            return True
        # First, move new cron jobs from the scheduled queue into the cronjob
        # list.
        if now is None:
            now = int(time.time())
        while len(self._scheduledQueue) > 0:
            job = self._scheduledQueue.pull()
            if job.status is not interfaces.CANCELLED:
                self._insertCronJob(job, now)
        # Now get all jobs that should be done now or earlier; if there are
        # any that do not have errors or are cancelled, then we have jobs to
        # do.
        for key in self._scheduledJobs.keys(max=now):
            jobs = [job for job in self._scheduledJobs[key]
                    if job.status not in (interfaces.CANCELLED,
                                          interfaces.ERROR)]
            if jobs:
                return True
        return False

    def claimNextJob(self, now=None):
        """
        claim next hob
        """
        job = self._pullJob(now)
        return job and job.id or None

    def processNext(self, now=None, jobid=None):
        """
        process next job in the queue
        """
        if jobid is None:
            job = self._pullJob(now)
        else:
            job = self.jobs[jobid]
        if job is None:
            return False
        if job.status == interfaces.COMPLETED:
            return True
        try:
            jobtask = component.getUtility(self.taskInterface, name=job.task)
        except ComponentLookupError, error:
            log.error('Task "%s" not found!' % job.task)
            log.exception(error)
            job.error = error
            if job.status != interfaces.CRONJOB:
                job.status = interfaces.ERROR
            return True
        job.started = datetime.datetime.now()
        if not hasattr(storage, 'runCount'):
            storage.runCount = 0
        storage.runCount += 1
        try:
            job.output = jobtask(self, job.id, job.input)
            if job.status != interfaces.CRONJOB:
                job.status = interfaces.COMPLETED
        except task.TaskError, error:
            job.error = error
            if job.status != interfaces.CRONJOB:
                job.status = interfaces.ERROR
        except Exception, error:
            if storage.runCount <= 3:
                log.error('Caught a generic exception, preventing thread '
                          'from crashing')
                log.exception(str(error))
                raise
            else:
                job.error = error
                if job.status != interfaces.CRONJOB:
                    job.status = interfaces.ERROR
                else:
                    storage.runCount = 0
        job.completed = datetime.datetime.now()
        return True

    def process(self, now=None):
        """See interfaces.ITaskService"""
        while self.processNext(now):
            pass

    def _pullJob(self, now=None):
        # first move new cron jobs from the scheduled queue into the cronjob
        # list
        if now is None:
            now = int(time.time())
        while len(self._scheduledQueue) > 0:
            job = self._scheduledQueue.pull()
            if job.status is not interfaces.CANCELLED:
                self._insertCronJob(job, now)
        # try to get the next cron job
        while True:
            try:
                first = self._scheduledJobs.minKey()
            except ValueError:
                break
            else:
                if first > now:
                    break
                jobs = self._scheduledJobs[first]
                job = jobs[0]
                self._scheduledJobs[first] = jobs[1:]
                if len(self._scheduledJobs[first]) == 0:
                    del self._scheduledJobs[first]
                if (job.status != interfaces.CANCELLED
                    and job.status != interfaces.ERROR):
                    if job.status != interfaces.DELAYED:
                        self._insertCronJob(job, now)
                    return job
        # get a job from the input queue
        if self._queue:
            return self._queue.pull()
        return None

    def _insertCronJob(self, job, now):
        for callTime, scheduled in list(self._scheduledJobs.items()):
            if job in scheduled:
                scheduled = list(scheduled)
                scheduled.remove(job)
                if len(scheduled) == 0:
                    del self._scheduledJobs[callTime]
                else:
                    self._scheduledJobs[callTime] = tuple(scheduled)
                break
        nextCallTime = job.timeOfNextCall(now)
        job.scheduledFor = datetime.datetime.fromtimestamp(nextCallTime)
        set = self._scheduledJobs.get(nextCallTime)
        if set is None:
            self._scheduledJobs[nextCallTime] = ()
        jobs = self._scheduledJobs[nextCallTime]
        self._scheduledJobs[nextCallTime] = jobs + (job,)

    def _generateId(self):
        """Generate an id which is not yet taken.

        This tries to allocate sequential ids so they fall into the
        same BTree bucket, and randomizes if it stumbles upon a
        used one.
        """
        while True:
            if self._v_nextid is None:
                self._v_nextid = random.randrange(0, self.maxint)
            uid = self._v_nextid
            self._v_nextid += 1
            if uid not in self.jobs:
                return uid
            self._v_nextid = None

    def startProcessing(self):
        """See interfaces.ITaskService"""
        if self.__parent__ is None:
            return
        if self._scheduledJobs is None:
            self._scheduledJobs = self.containerClass()
        if self._scheduledQueue is None:
            self._scheduledQueue = zc.queue.PersistentQueue()
        # Create the path to the service within the DB.
        servicePath = self.getServicePath()
        log.info('starting service %s' % ".".join(servicePath))
        # Start the thread running the processor inside.
        #
        db = z3c.taskqueue.GLOBALDB
        if db is None:
            raise ValueError('z3c.taskqueue.GLOBALDB is not initialized; '
                'should be done with IDatabaseOpenedWithRootEvent')
        processor = self.processorFactory(
            db, servicePath, **self.processorArguments)
        threadName = self._threadName()
        thread = threading.Thread(target=processor, name=threadName)
        thread.setDaemon(True)
        thread.running = True
        thread.start()

    def stopProcessing(self):
        """See interfaces.ITaskService"""
        if self.__name__ is None:
            return
        servicePath = self.getServicePath()
        log.info('stopping service %s' % ".".join(servicePath))
        threadName = self._threadName()
        for thread in threading.enumerate():
            if thread.getName() == threadName:
                thread.running = False
                break

    def isProcessing(self):
        """See interfaces.ITaskService"""
        if self.__name__ is not None:
            name = self._threadName()
            for thread in threading.enumerate():
                if thread.getName() == name:
                    if thread.running:
                        return True
                    break
        return False

    def getServicePath(self):
        raise NotImplemented

    THREADNAME_PREFIX = 'taskqueue'

    def _threadName(self):
        """Return name of the processing thread."""
        # This name isn't unique based on the path to self, but this doesn't
        # change the name that's been used in past versions.
        path = self.getServicePath()
        path.insert(0, self.THREADNAME_PREFIX)
        return '.'.join(path)
