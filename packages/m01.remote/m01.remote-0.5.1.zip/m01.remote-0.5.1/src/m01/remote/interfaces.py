###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Interfaces
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
import zope.i18nmessageid

import m01.mongo.interfaces
import m01.mongo.schema

_ = zope.i18nmessageid.MessageFactory('p01')

QUEUED = u'queued'
PROCESSING = u'processing'
CANCELLED = u'cancelled'
COMPLETED = u'completed'
ERROR = u'error'

JOB_STATUS_NAMES = [
    QUEUED,
    PROCESSING,
    CANCELLED,
    COMPLETED,
    ERROR,
]


class IRemoteProcessor(zope.interface.Interface):
    """A compoent for managing and executing long-running, remote process."""

    isProcessing = zope.schema.Bool(
            title=_(u'Is processing'),
            description=_(u'Is processing'),
            default=False,
            )

    isScheduling = zope.schema.Bool(
            title=_(u'Is scheduling'),
            description=_(u'Is scheduling'),
            default=False,
            )

    processorStartTime = zope.schema.Time(
            title=_(u'Processor start time'),
            description=_(u'Processor start time'),
            default=None,
            )

    schedulerStartTime = zope.schema.Time(
            title=_(u'Scheduler start time'),
            description=_(u'Scheduler start time'),
            default=None,
            )

    def getRemoteProcessorJobFactoryCollection():
        """Returns the mongodb job factory collection"""

    def getRemoteProcessorJobCollection():
        """Returns the mongodb job collection"""

    def getRemoteProcessorSchedulerCollection():
        """Returns the mongodb scheduler collection"""

    def addJobFactory(name, job):
        """Add a new job by the given job name.

        * name argument is a string specifying the (named) job.
        * input are arguments for job processing.
          to be started later with calling processJob
        """

    def addJob(name, input=None):
        """Add an available job by the given job name to the processor.

        * name argument is a string specifying the job by it's name.
        * input are arguments for job processing.
        """

    def removeJobs(stati=None):
        """Remove all jobs which are completed or canceled or have errors by
        the given stati.
        
        If no stati is given all stati are used for abort jobs. Note: abortJobs
        will remove jobs from the processor but not remove the original job
        object.
        """

    def cancelJob(jobid):
        """Cancel a particular job."""

    def getJobStatus(jobid):
        """Get the status of a job."""

    def getJobResult(jobid):
        """Get the result data structure of the job."""

    def getJobErrors(jobid):
        """Get the list of job error message strings."""

    # worker API
    def pullNextJob(jobQuery=None, now=None):
        """Pull next job.

        The jobQuery value must be a dict or None. None means non filtered jobs.
        """

    def processNextJob(jobQuery=None, now=None):
        """Process the next job in the queue.

        The jobQuery value must be a dict or None. None means non filtered jobs.

        This method get called from a worker thread.
        """

    def processJobs(jobQuery=None, now=None):
        """Process all scheduled jobs which will fit for the given query.

        The jobQuery value must be a dict or None. None means non filtered jobs.

        Note: this call blocks the thread it is running in.
        """

    # scheduler API
    def addScheduler(item):
        """Add scheduler item."""

    def scheduleNextJob(callTime=None):
        """Schedule next job"""

    def reScheduleItem(item, callTime=None):
        """Re-schedule item."""

    def reScheduleItems(callTime=None):
        """Re-schedule items."""

    # worker start/stop API
    def startProcessor():
        """Start processing jobs"""

    def stopProcessor():
        """Stop processing jobs"""

    # scheduler start/stop API
    def startScheduler():
        """Start scheduling jobs."""

    def stopScheduler():
        """Stop scheduling jobs."""


class IJobFactories(m01.mongo.interfaces.IMongoContainer):
    """Mongo job factory container."""


class IJobs(m01.mongo.interfaces.IMongoContainer):
    """Mongo job container."""

    def add(job):
        """Add a job with it's given __name__"""

    def updateRetryTime(data, callTime=None):
        """Update retry time

        The retryTime concept solves two use cases.

        1. we use an atomic operation ($set) for set the new retryTime
           This will ensure that only our process can pick the given job
           if the retryTime get set. All other (multi) processing worker
           can't pick this updated job

        2. if the job raises an error (everything except JobError) the job
           get picked again if the previous updated retryTime expires.
           Note: if you raise a JobError the processor will set the status
           to error and skip future (retry) processing

        """

    def getNextQueuedItem(jobQuery=None, callTime=None):
        """Get the next queued item"""

    def pullNextJob(jobQuery=None, callTime=None):
        """Pull next job"""


class IJob(m01.mongo.interfaces.IMongoContainerItem):
    """Job used as job factory and job.

    A job factoy instance can clone it's self and creat a job with additional
    input data.
    
    Note: a job needs to implement additional attributes if optinal data get
    used as job input. Take care that you NEVER use existing attribute names
    as new input data arguments or you will override existing job values if the
    input get applied during job creation! See: IJob.getJob method.

    """

    # implement your own specific output value concept, by default we only
    # handle valid mongodb data wihout validation etc.
    output = zope.schema.Field(
        title=u'Output',
        description=u'The output of a processed job.',
        required=False,
        default=None)

    jobName = zope.schema.TextLine(
        title=u'Job name',
        description=u'The job name reference',
        required=True
        )

    active = zope.schema.Bool(
        title=_(u'Active'),
        description=_(u'Marker for active scheduler items.'),
        default=True,
        required=True
        )

    retryTime = zope.schema.Datetime(
        title=_(u'Retry call time'),
        description=_(u'Time after another worker can try again'),
        required=False,
        )

    retryDelay = zope.schema.Int(
        title=_(u'Retry delay (second)'),
        description=_(u'Seconds after another worker can try again'),
        default=300,
        required=True
        )

    status = zope.schema.Choice(
        title=u'Status',
        description=u'The current status of the job.',
        values=JOB_STATUS_NAMES,
        required=True)

    retryCounter = zope.schema.Int(
        title=u'Retry counter',
        description=u'Retry counter',
        default=0,
        required=True)

    maxRetries = zope.schema.Int(
        title=u'Maximum Retries',
        description=u'Maximum Retries',
        default=3,
        required=True)

    errors = m01.mongo.schema.MongoList(
        title=u'Errors',
        description=u'A list of errors (one for each retry)',
        value_type = zope.schema.TextLine(
            title=u'Error',
            description=u'The error object when the job processing failed.',
            required=True),
        required=False,
        default=[])

    created = zope.schema.Datetime(
        title=u'Creation Date',
        description=u'The date/time at which the job was created.',
        required=True)

    queued = zope.schema.Datetime(
        title=u'Queued Date',
        description=u'The date/time at which the job was queued for processsing.',
        required=True)

    picked = zope.schema.Datetime(
        title=u'Picked Date',
        description=u'The date/time at which the job was picked from queue.')

    started = zope.schema.Datetime(
        title=u'Start Date',
        description=u'The date/time at which the job was started.')

    completed = zope.schema.Datetime(
        title=u'Completion Date',
        description=u'The date/time at which the job was completed.')

    def __call__(remoteProcessor):
        """Process a job."""


class IScheduler(m01.mongo.interfaces.IMongoStorage):
    """Scheduler manages scheduler items."""

    def reScheduleItem(item, callTime=None):
        """Re-schedule item."""

    def reScheduleItems(callTime=None):
        """Re-schedule items."""

    def pullNextSchedulerItem(now=None):
        """Get next pending scheduler item based on now and the scheduled time.
        """


class ISchedulerItem(m01.mongo.interfaces.IMongoStorageItem):
    """Based scheduler item."""

    # implement your own specific input value concept, by default we only
    # handle valid mongodb data wihout validation etc.
    input = zope.schema.Field(
        title=u'Input',
        description=u'The input for processing a job.',
        required=False)

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title'),
        required=True
        )

    description = zope.schema.Text(
        title=_(u'Description'),
        description=_(u'Description'),
        required=False
        )

    jobName = zope.schema.TextLine(
        title=_(u'Job name'),
        description=_(u'Job name'),
        required=True
        )

    active = zope.schema.Bool(
        title=_(u'Active Scheduler'),
        description=_(u'Marker for active scheduler items.'),
        default=False,
        required=True
        )

    nextCallTime = zope.schema.Datetime(
        title=_(u'Next call time'),
        description=_(u'Next call time'),
        required=False,
        )

    retryTime = zope.schema.Datetime(
        title=_(u'Retry call time'),
        description=_(u'Time after another worker can try again'),
        required=False,
        )

    retryDelay = zope.schema.Int(
        title=_(u'Retry delay (second)'),
        description=_(u'Seconds after another worker can try again'),
        default=300,
        required=True
        )

    def getNextCallTime(now):
        """Returns the next call time if smaller then the given callTime.
        
        This method is also responsible for update the nextCallTime which get
        used for compare the next call time if this method returns a timestamp.

        Note ``next`` means not that the result must be in the future. It could
        be or not. It's just the next call time calculated if by the ``last``
        getNextCallTime call. The nextCallTime value is caching this last call
        value.

        How does this work:

        If the next call time is before the given call time, calculate the
        next call time and return the previous next call time. If the next
        call time is after the call time, return the stored next call time.

        This will ensure that we never miss a call between the last call time
        and the current call time. This concept does not only ensure that we
        skip more the one missed call between the last call time and the next
        call time. This will also ensure that we do not too often calculate the
        next call time. We only calculate the next call time if absolutly
        needed.

        """


class IDelay(ISchedulerItem):
    """Delay based scheduler item."""

    # Note: retryDelay must be smaller then the delay or the job will scheduled
    # after the retryDelay expires not only the delay.
    # Note: the delay should not be smaller then the process takes
    delay = zope.schema.Int(
        title=_(u'delay (second)'),
        description=_(u'delay (second)'),
        default=0,
        required=False
        )


class ICron(ISchedulerItem):
    """Scheduler parameter for IJob."""

    minute = m01.mongo.schema.MongoList(
        title=_(u'Minute(s) (0 - 59)'),
        description=_(u'Minute(s)'),
        value_type=zope.schema.Int(
            title=_(u'Minute'),
            description=_(u'Minute'),
            min=0,
            max=59,
            ),
        default=[],
        required=False
        )

    hour = m01.mongo.schema.MongoList(
        title=_(u'Hour(s) (0 - 23)'),
        description=_(u'Hour(s)'),
        value_type=zope.schema.Int(
            title=_(u'Hour'),
            description=_(u'Hour'),
            min=0,
            max=23,
            ),
        default=[],
        required=False
        )

    dayOfWeek = m01.mongo.schema.MongoList(
        title=_(u'Day of week (0 - 6)'),
        description=_(u'Day of week'),
        value_type=zope.schema.Int(
            title=_(u'Day of week'),
            description=_(u'Day of week'),
            min=0,
            max=6,
            ),
        default=[],
        required=False
        )

    dayOfMonth = m01.mongo.schema.MongoList(
        title=_(u'Day of month (1 - 31)'),
        description=_(u'Day of month'),
        value_type=zope.schema.Int(
            title=_(u'Day of month'),
            description=_(u'Day of month'),
            min=1,
            max=31,
            ),
        default=[],
        required=False
        )

    month = m01.mongo.schema.MongoList(
        title=_(u'Month(s) (1 - 12)'),
        description=_(u'Month(s)'),
        value_type=zope.schema.Int(
            title=_(u'Month'),
            description=_(u'Month'),
            min=1,
            max=12,
            ),
        default=[],
        required=False
        )


class IWorker(zope.interface.Interface):
    """Job Worker

    Process the jobs that are waiting in the queue. A worker is meant to
    be run in a separate thread. To complete a job, it simply calls back into
    the remote queue. This works, since it does not use up any Web server
    threads.

    Processing a job can take a long time. However, we do not have to worry
    about transaction conflicts, since no other request is touching the job
    object. But be careful it's always possible that if the job manipulates
    something that this could force to run into a conflict error.

    """

    running = zope.schema.Bool(
        title=_(u"Running Flag"),
        description=_(u"Tells whether the worker is currently running."),
        readonly=True)

    def __call__():
        """Run the worker."""


class ISchedulerWorker(IWorker):
    """Worker which schedules jobs"""

    def __init__(remoteProcessor, waitTime=1.0):
        """Initialize the worker"""


class ISimpleJobWorker(IWorker):
    """Worker which processes jobs"""

    def __init__(remoteProcessor, jobQuery=None, waitTime=1.0):
        """Initialize the worker"""


class IMultiJobWorker(IWorker):
    """Worker which processes jobs"""

    def __init__(remoteProcessor, jobQuery=None, waitTime=1.0, maxThreads=1):
        """Initialize the worker with waitTime and maxThreads"""


class IJobNameTermsAware(zope.interface.Interface):
    """Force to use a select field for our jobName selection."""


class IJobErrorMessage(zope.interface.Interface):
    """Job error to message converter"""
