=====================
Remote Task Execution
=====================

.. contents::

This package provides an implementation of a task queue service
It is also possible to run cron jobs at specific times.

Usage
_____

  >>> STOP_SLEEP_TIME = 0.02

Let's now start by creating a single service:

  >>> from z3c import taskqueue
  >>> service = taskqueue.service.TaskService()

We can discover the available tasks:

  >>> service.getAvailableTasks()
  {}

This list is initially empty, because we have not registered any tasks. Let's
now define a task that simply echos an input string:

  >>> def echo(input):
  ...     return input

  >>> echoTask = taskqueue.task.SimpleTask(echo)

The only API requirement on the converter is to be callable. Now we make sure
that the task works:

  >>> echoTask(service, 1, input={'foo': 'blah'})
  {'foo': 'blah'}

Let's now register the task as a utility:

  >>> import zope.component
  >>> zope.component.provideUtility(echoTask, name='echo')

The echo task is now available in the service:

  >>> service.getAvailableTasks()
  {u'echo': <SimpleTask <function echo ...>>}

Since the service cannot instantaneously complete a task, incoming jobs are
managed by a queue. First we request the echo task to be executed:

  >>> jobid = service.add(u'echo', {'foo': 'bar'})
  >>> jobid
  1392637175

The ``add()`` function schedules the task called "echo" to be executed with
the specified arguments. The method returns a job id with which we can inquire
about the job.
By default the ``add()`` function adds and starts the job ASAP. Sometimes we need
to have a jobid but not to start the job yet. See startlater.txt how.

  >>> service.getStatus(jobid)
  'queued'

Since the job has not been processed, the status is set to "queued". Further,
there is no result available yet:

  >>> service.getResult(jobid) is None
  True

As long as the job is not being processed, it can be cancelled:

  >>> service.cancel(jobid)
  >>> service.getStatus(jobid)
  'cancelled'

Let's add another job:

  >>> jobid = service.add(u'echo', {'foo': 'bar'})
  >>> service.processNext()
  True

  >>> service.getStatus(jobid)
  'completed'
  >>> service.getResult(jobid)
  {'foo': 'bar'}

Now, let's define a new task that causes an error:

  >>> def error(input):
  ...     raise taskqueue.task.TaskError('An error occurred.')

  >>> zope.component.provideUtility(
  ...     taskqueue.task.SimpleTask(error), name='error')

Now add and execute it:

  >>> jobid = service.add(u'error')
  >>> service.processNext()
  True

Let's now see what happened:

  >>> service.getStatus(jobid)
  'error'
  >>> service.getError(jobid)
  'An error occurred.'

For management purposes, the service also allows you to inspect all jobs:

  >>> dict(service.jobs)
  {1392637176: <Job 1392637176>, 1392637177: <Job 1392637177>, 1392637175: <Job 1392637175>}


To get rid of jobs not needed anymore one can use the clean method.

  >>> jobid = service.add(u'echo', {'blah': 'blah'})
  >>> sorted([job.status for job in service.jobs.values()])
  ['cancelled', 'completed', 'error', 'queued']

  >>> service.clean()

  >>> sorted([job.status for job in service.jobs.values()])
  ['queued']


Cron jobs
---------

Cron jobs execute on specific times.

  >>> import time
  >>> from z3c.taskqueue.job import CronJob
  >>> now = 0
  >>> time.gmtime(now)
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)

We set up a job to be executed once an hour at the current minute. The next
call time is the one our from now.

Minutes

  >>> cronJob = CronJob(-1, u'echo', (), minute=(0, 10))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=10, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)
  >>> time.gmtime(cronJob.timeOfNextCall(10*60))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=1, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)

Hour

  >>> cronJob = CronJob(-1, u'echo', (), hour=(2, 13))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=2, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)
  >>> time.gmtime(cronJob.timeOfNextCall(2*60*60))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=13, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)

Month

  >>> cronJob = CronJob(-1, u'echo', (), month=(1, 5, 12))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  time.struct_time(tm_year=1970, tm_mon=5, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=4, tm_yday=121, tm_isdst=0)
  >>> time.gmtime(cronJob.timeOfNextCall(cronJob.timeOfNextCall(0)))
  time.struct_time(tm_year=1970, tm_mon=12, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=1, tm_yday=335, tm_isdst=0)

Day of week [0..6], jan 1 1970 is a wednesday.

  >>> cronJob = CronJob(-1, u'echo', (), dayOfWeek=(0, 2, 4, 5))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=2, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=4, tm_yday=2, tm_isdst=0)
  >>> time.gmtime(cronJob.timeOfNextCall(60*60*24))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=3, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=5, tm_yday=3, tm_isdst=0)
  >>> time.gmtime(cronJob.timeOfNextCall(2*60*60*24))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=5, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=0, tm_yday=5, tm_isdst=0)
  >>> time.gmtime(cronJob.timeOfNextCall(4*60*60*24))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=7, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=2, tm_yday=7, tm_isdst=0)

DayOfMonth [1..31]

  >>> cronJob = CronJob(-1, u'echo', (), dayOfMonth=(1, 12, 21, 30))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=12, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=0, tm_yday=12, tm_isdst=0)
  >>> time.gmtime(cronJob.timeOfNextCall(12*24*60*60))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=21, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=2, tm_yday=21, tm_isdst=0)

Combined

  >>> cronJob = CronJob(-1, u'echo', (), minute=(10,),
  ...                                 dayOfMonth=(1, 12, 21, 30))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=10, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)
  >>> time.gmtime(cronJob.timeOfNextCall(10*60))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=1, tm_min=10, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)

  >>> cronJob = CronJob(-1, u'echo', (), minute=(10,),
  ...                                 hour=(4,),
  ...                                 dayOfMonth=(1, 12, 21, 30))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=4, tm_min=10, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)
  >>> time.gmtime(cronJob.timeOfNextCall(10*60))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=4, tm_min=10, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)


A cron job can also be used to delay the execution of a job.

  >>> cronJob = CronJob(-1, u'echo', (), delay=10,)
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=10, tm_wday=3, tm_yday=1, tm_isdst=0)
  >>> time.gmtime(cronJob.timeOfNextCall(1))
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=11, tm_wday=3, tm_yday=1, tm_isdst=0)


Creating Delayed Jobs
---------------------

A delayed job is executed once after the given delay time in seconds.

  >>> count = 0
  >>> def counting(input):
  ...     global count
  ...     count += 1
  ...     return count
  >>> countingTask = taskqueue.task.SimpleTask(counting)
  >>> zope.component.provideUtility(countingTask, name='counter')

  >>> jobid = service.addCronJob(u'counter',
  ...                            {'foo': 'bar'},
  ...                            delay = 10,
  ...                           )
  >>> service.getStatus(jobid)
  'delayed'
  >>> service.processNext(0)
  True
  >>> service.getStatus(jobid)
  'delayed'
  >>> service.processNext(9)
  False
  >>> service.getStatus(jobid)
  'delayed'

At 10 seconds the job is executed and completed.

  >>> service.processNext(10)
  True
  >>> service.getStatus(jobid)
  'completed'


Creating Cron Jobs
------------------

Here we create a cron job which runs 10 minutes and 13 minutes past the hour.

  >>> count = 0

  >>> jobid = service.addCronJob(u'counter',
  ...                            {'foo': 'bar'},
  ...                            minute = (10, 13),
  ...                           )
  >>> service.getStatus(jobid)
  'cronjob'

We process the remote task but our cron job is not executed because we are too
early in time.

  >>> service.processNext(0)
  False
  >>> service.getStatus(jobid)
  'cronjob'
  >>> service.getResult(jobid) is None
  True

Now we run the remote task 10 minutes later and get a result.

  >>> service.processNext(10*60)
  True
  >>> service.getStatus(jobid)
  'cronjob'
  >>> service.getResult(jobid)
  1

And 1 minutes later it is not called.

  >>> service.processNext(11*60)
  False
  >>> service.getResult(jobid)
  1

But 3 minutes later it is called again.

  >>> service.processNext(13*60)
  True
  >>> service.getResult(jobid)
  2

A job can be rescheduled.

  >>> job = service.jobs[jobid]
  >>> job.update(minute = (11, 13))

After the update the job must be rescheduled in the service.

  >>> service.reschedule(jobid)

Now the job is not executed at the old registration minute which was 10.

  >>> service.processNext(10*60+60*60)
  False
  >>> service.getResult(jobid)
  2

But it executes at the new minute which is set to 11.

  >>> service.processNext(11*60+60*60)
  True
  >>> service.getResult(jobid)
  3

Check Interfaces and stuff
--------------------------

  >>> from z3c.taskqueue import interfaces
  >>> from zope.interface.verify import verifyClass, verifyObject
  >>> verifyClass(interfaces.ITaskService, taskqueue.service.TaskService)
  True
  >>> verifyObject(interfaces.ITaskService, service)
  True
  >>> interfaces.ITaskService.providedBy(service)
  True

  >>> from z3c.taskqueue.job import Job
  >>> fakejob = Job(1, u'echo', {})
  >>> verifyClass(interfaces.IJob, Job)
  True
  >>> verifyObject(interfaces.IJob, fakejob)
  True
  >>> interfaces.IJob.providedBy(fakejob)
  True

  >>> fakecronjob = CronJob(1, u'echo', {})
  >>> verifyClass(interfaces.ICronJob, CronJob)
  True
  >>> verifyObject(interfaces.ICronJob, fakecronjob)
  True
  >>> interfaces.IJob.providedBy(fakecronjob)
  True
