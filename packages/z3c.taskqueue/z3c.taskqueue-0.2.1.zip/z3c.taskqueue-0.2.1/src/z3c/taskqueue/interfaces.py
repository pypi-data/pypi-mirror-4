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
"""Task Service Interfaces

$Id$
"""
__docformat__ = 'restructuredtext'
from zope import interface
from zope import schema
from zope.configuration import fields
from zope.container.interfaces import IContained

QUEUED = 'queued'
PROCESSING = 'processing'
CANCELLED = 'cancelled'
ERROR = 'error'
COMPLETED = 'completed'
DELAYED = 'delayed'
CRONJOB = 'cronjob'
DELAYED = 'delayed'
STARTLATER = 'start later'


class ITask(interface.Interface):
    """A task available in the task service"""

    inputSchema = schema.Object(
        title=u'Input Schema',
        description=u'A schema describing the task input signature.',
        schema=interface.Interface,
        required=False)

    outputSchema = schema.Object(
        title=u'Output Schema',
        description=u'A schema describing the task output signature.',
        schema=interface.Interface,
        required=False)

    def __call__(service, jobid, input):
        """Execute the task.

        The ``service`` argument is the task service object. It allows access
        to service wide data and the system as a whole.

        Tasks do not live in a vacuum, but are tightly coupled to the job
        executing it. The ``jobid`` argument provides the id of the job being
        processed.

        The ``input`` object must conform to the input schema (if
        specified). The return value must conform to the output schema.
        """


class ITaskService(IContained):
    """A service for managing and executing tasks."""

    jobs = schema.Object(
        title=u'Jobs',
        description=u'A mapping of all jobs by job id.',
        schema=interface.common.mapping.IMapping)

    taskInterface = fields.GlobalInterface(
            title=u'Task Interface',
            description=u'The interface to lookup task utilities',
            default=ITask,
            )

    def getAvailableTasks():
        """Return a mapping of task name to the task."""

    def add(task, input=None, startLater=False):
        """Add a new job for the specified task.

        * task argument is a string specifying the task.
        * input are arguments for the task.
        * startLater, if True job will be added (gets a jobid) but needs
          to be started with startJob later
        """

    def addCronJob(task, input,
                   minute=(),
                   hour=(),
                   dayOfMonth=(),
                   month=(),
                   dayOfWeek=(),
                  ):
        """Add a new cron job."""

    def startJob(jobid):
        """Start a job previously added job with add(..., startLater=True)
        """

    def reschedule(jobid):
        """Rescheudle a cron job.

        This is neccessary if the cron jobs parameters are changed.
        """

    def clean(status=[CANCELLED, ERROR, COMPLETED]):
        """removes all jobs which are completed or canceled or have errors."""

    def cancel(jobid):
        """Cancel a particular job."""

    def getStatus(jobid):
        """Get the status of a job."""

    def getResult(jobid):
        """Get the result data structure of the job."""

    def getError(jobid):
        """Get the error of the job."""

    def hasJobsWaiting(now=None):
        """Determine whether there are jobs that need to be processed.

        Returns a simple boolean.
        """

    def processNext():
        """Process the next job in the queue."""

    def process():
        """Process all scheduled jobs.

        This call blocks the thread it is running in.
        """

    def startProcessing():
        """Start processing jobs.

        This method has to be called after every server restart.
        """

    def stopProcessing():
        """Stop processing jobs."""

    def isProcessing():
        """Check whether the jobs are being processed.

        Return a boolean representing the state.
        """


class IJob(interface.Interface):
    """An internal job object."""

    id = schema.Int(
        title=u'Id',
        description=u'The job id.',
        required=True)

    task = schema.TextLine(
        title=u'Task',
        description=u'The task to be completed.',
        required=True)

    status = schema.Choice(
        title=u'Status',
        description=u'The current status of the job.',
        values=[QUEUED, PROCESSING, CANCELLED, ERROR,
                COMPLETED, DELAYED, CRONJOB, STARTLATER],
        required=True)

    input = schema.Object(
        title=u'Input',
        description=u'The input for the task.',
        schema=interface.Interface,
        required=False)

    output = schema.Object(
        title=u'Output',
        description=u'The output of the task.',
        schema=interface.Interface,
        required=False,
        default=None)

    error = schema.Object(
        title=u'Error',
        description=u'The error object when the task failed.',
        schema=interface.Interface,
        required=False,
        default=None)

    created = schema.Datetime(
        title=u'Creation Date',
        description=u'The date/time at which the job was created.',
        required=True)

    started = schema.Datetime(
        title=u'Start Date',
        description=u'The date/time at which the job was started.')

    completed = schema.Datetime(
        title=u'Completion Date',
        description=u'The date/time at which the job was completed.')


class ICronJob(IJob):
    """Parameters for cron jobs"""

    minute = schema.Tuple(
            title=u'minute(s)',
            default=(),
            required=False,
            )

    hour = schema.Tuple(
            title=u'hour(s)',
            default=(),
            required=False,
            )

    dayOfMonth = schema.Tuple(
            title=u'day of month',
            default=(),
            required=False,
            )

    month = schema.Tuple(
            title=u'month(s)',
            default=(),
            required=False,
            )

    dayOfWeek = schema.Tuple(
            title=u'day of week',
            default=(),
            required=False,
            )

    delay = schema.Int(
            title=u'delay',
            default=0,
            required=False,
            )

    scheduledFor = schema.Datetime(
            title=u'scheduled',
            default=None,
            required=False,
            )

    def update(minute, hour, dayOfMonth, month, dayOfWeek, delay):
        """Update the cron job.

        The job must be rescheduled in the containing service.
        """

    def timeOfNextCall(now=None):
        """Calculate the time for the next call of the job.

        now is a convenience parameter for testing.
        """


class IProcessor(interface.Interface):
    """Job Processor

    Process the jobs that are waiting in the queue. A processor is meant to
    be run in a separate thread. To complete a job, it simply calls back into
    the task server. This works, since it does not use up any Web server
    threads.

    Processing a job can take a long time. However, we do not have to worry
    about transaction conflicts, since no other request is touching the job
    object.
    """

    running = schema.Bool(
        title=u"Running Flag",
        description=u"Tells whether the processor is currently running.",
        readonly=True)

    def __call__(db, servicePath):
        """Run the processor.

        The ``db`` is a ZODB instance that is used to call back into the task
        service. The ``servicePath`` specifies how to traverse to the task
        service itself.
        """
