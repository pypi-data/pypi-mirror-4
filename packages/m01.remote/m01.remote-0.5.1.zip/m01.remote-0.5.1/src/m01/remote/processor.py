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
"""Remote processor
$Id:$
"""
__docformat__ = "reStructuredText"

import os
import sys
import datetime
import logging
import threading
import time

import zope.interface

import m01.remote.job
import m01.remote.worker
import m01.remote.scheduler
import m01.remote.exceptions
from m01.mongo import UTC
from m01.remote import interfaces

try:
    import multiprocessing
    cpu_count = multiprocessing.cpu_count
except ImportError:
    def cpu_count():
        """Returns the number of available CPUs"""
        num = 1
        try:
            if sys.platform == 'win32':
                num = int(os.environ['NUMBER_OF_PROCESSORS'])
            elif 'bsd' in sys.platform or sys.platform == 'darwin':
                num = int(os.popen('sysctl -n hw.ncpu').read())
            else:
                num = os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, KeyError, OSError, AttributeError):
            return 1

        return num and num or 1


log = logging.getLogger('m01.remote')

CPU_COUNT = cpu_count()
log.info("Processor CPU_COUNT '%s'" % CPU_COUNT)


class RemoteProcessor(object):
    """Remote processor.

    The RemoteProcessor is not persistent and normaly get used as an appliction
    root object. There is nothing which we need to store in a database.
    All items are located in their relevant mongo collection.
    This means the RemoteProcessor is just a storage and execution API.

    This also means the RemoteProcessor can get used as a WSGI application
    root.

    The remote queue uses local IJob component for processing. Such job
    objects get cloned if we need to process one.

    Some internals:

    _jobFactories -- stores the original job objects. This jobs are the master
      which get cloned if we need to process one.

    _jobs -- stores all processing jobs. This allows us to get a job by id.

    _scheduler -- stores scheduled items which know when a job should get
      processed. Jobs created by a scheduler will get processed without to
      mark them as scheduled.

    """
    zope.interface.implements(interfaces.IRemoteProcessor)

    # job worker
    jobWorkerFactory = m01.remote.worker.SimpleJobWorker
    jobWorkerArguments = {'jobQuery': None,
                          'waitTime': 1.0,
                          'maxThreads': CPU_COUNT}
    processorStartTime = None

    # scheduler worker
    schedulerWorkerFactory = m01.remote.worker.SchedulerWorker
    schedulerWorkerArguments = {'waitTime': 1.0}
    schedulerStartTime = None

    __name__ = __parent__ = None

    def __init__(self):
        # setup storages using mongodb collections
        self._jobFactories = m01.remote.job.JobFactories(self)
        self._jobFactories.__parent__ = self
        self._jobs = m01.remote.job.Jobs(self)
        self._jobs.__parent__ = self
        self._scheduler = m01.remote.scheduler.Scheduler(self)
        self._scheduler.__parent__ = self

    def getRemoteProcessorDB(self):
        """Returns a mongodb collection"""
        raise NotImplementedError(
            "Subclass must implement getRemoteProcessorDB")

    def getRemoteProcessorJobFactoryCollection(self):
        """Returns the mongodb job factory collection"""
        db = self.getRemoteProcessorDB()
        return db.rfactories

    def getRemoteProcessorJobCollection(self):
        """Returns the mongodb job collection"""
        db = self.getRemoteProcessorDB()
        return db.rjobs

    def getRemoteProcessorSchedulerCollection(self):
        """Returns the mongodb scheduler collection"""
        db = self.getRemoteProcessorDB()
        return db.rscheduler

    # mongo item loader used by storages
    def loadRemoteProcessorJobItems(self, data):
        """Load data into the relevant item type"""
        raise NotImplementedError(
            "Subclass must implement loadRemoteProcessorJobItems")

    # job factory API
    def addJobFactory(self, name, job):
        """Add a new job as available job."""
        self._jobFactories[name] = job

    def getJobFactory(self, name):
        return self._jobFactories.get(name, None)

    # job processor API
    def _createJob(self, name, input=None):
        """See interfaces.IRemoteProcessor"""
        orgJob = self._jobFactories.get(name)
        if orgJob is None:
            raise ValueError("Job with given name '%s' does not exist" % name)
        # clone and return job
        return orgJob.getJob(input)

    def addJob(self, name, input=None):
        """See interfaces.IRemoteProcessor
        
        Note: this method should be responsible if a job get really added or 
        not. But such rules depend on your application which means you need
        to implement an own pattern which could prevent to add more jobs then
        the processor can process.
        """
        job = self._createJob(name, input)
        self._jobs.add(job)
        # just mark them as queued, the next worker will pickup this job
        job.queued = datetime.datetime.now(UTC)
        job.status = interfaces.QUEUED
        return job.__name__

    def removeJobs(self, stati=None, allowed=None):
        """See interfaces.IRemoteProcessor"""
        if allowed is None:
            # you are your own riks if we remove another stati the the allowed
            allowed = [interfaces.CANCELLED, interfaces.ERROR, interfaces.COMPLETED]
        if stati is None:
            stati = allowed
        if not isinstance(stati, list):
            stati = [stati]
        # first check if we do not have bad stati
        for status in stati:
            if status not in allowed:
                raise ValueError("Can't remove jobs with status %s" % status)
        # now remove all items from mongodb without transaction support
        # (we don't like to load a large set of items just for remove them)
        res = {}
        jobs = self._jobs
        collection = self._jobs.collection
        for status in stati:
            # check if we have jobs in our add cache
            for obj in list(jobs._cache_added.values()):
                if obj.status == status:
                    del jobs._cache_added[obj.__name__]
            # check if we have jobs in our load cache
            for obj in list(jobs._cache_loaded.values()):
                if obj.status == status:
                    del jobs._cache_loaded[obj.__name__]
            # check if we have jobs in our remove cache
            for obj in list(jobs._cache_removed.values()):
                if obj.status == status:
                    del jobs._cache_removed[obj.__name__]
            # now remove all items by status from mongodb but only four our
            # server
            spec = {'status': status}
            jobQuery = self.jobWorkerArguments.get('jobQuery')
            if jobQuery is not None:
                # apply jobQuery as filter
                spec.update(jobQuery)
            res[status] = collection.find(spec).count()
            collection.remove(spec)
        return res

    def cancelJob(self, jobid):
        """See interfaces.IRemoteProcessor"""
        # set status to cancelled
        if jobid in self._jobs:
            job = self._jobs[jobid]
            if job.status in [interfaces.QUEUED, interfaces.PROCESSING]:
                job.status = interfaces.CANCELLED

    def getJobStatus(self, jobid):
        """See interfaces.IRemoteProcessor"""
        return self._jobs[jobid].status

    def getJobResult(self, jobid):
        """See interfaces.IRemoteProcessor"""
        return self._jobs[jobid].output

    def getJobErrors(self, jobid):
        """See interfaces.IRemoteProcessor"""
        return self._jobs[jobid].errors

    # scheduler API
    def addScheduler(self, item):
        """Add a new scheduler item."""
        return self._scheduler.add(item)

    def scheduleNextJob(self, callTime=None):
        """Schedule next job"""
        # return the next job
        if callTime is None:
            callTime = datetime.datetime.now(UTC)
        # get next scheduled item
        item = self._scheduler.pullNextSchedulerItem(callTime)
        if item is not None:
            # create a job, mark them as queued and return the job.__name__.
            return self.addJob(item.jobName, item.input)

    def reScheduleItem(self, item, callTime=None):
        """Re-schedule an item"""
        if callTime is None:
            callTime = datetime.datetime.now(UTC)
        self._scheduler.reScheduleItem(item, callTime)

    def reScheduleItems(self, callTime=None):
        """Re-schedule all items"""
        if callTime is None:
            callTime = datetime.datetime.now(UTC)
        self._scheduler.reScheduleItems(callTime)

    # simple job worker API
    def pullNextJob(self, jobQuery=None, callTime=None):
        """Pull a pending job"""
        # return the next job
        if callTime is None:
            callTime = datetime.datetime.now(UTC)
        # return a queued job which marks them as processing or None
        return self._jobs.pullNextJob(jobQuery, callTime)

    # single processor job worker API
    def processNextJob(self, jobQuery=None, callTime=None):
        """This method get called by a simple worker."""
        job = self.pullNextJob(jobQuery, callTime)
        if job is None:
            return False
        return self._processJob(job)

    def processJobs(self, jobQuery=None, now=None):
        """See interfaces.IRemoteProcessor"""
        while self.processNextJob(jobQuery, now):
            pass

    # multi processor job worker API
    def processJob(self, jobid):
        """Process a job by it's id, can raise KeyError or TypeError"""
        job = self._jobs[jobid]
        return self._processJob(job)

    # internal helpers
    def _processJob(self, job):
        """Knows how to process a given job."""
        if job.status != interfaces.PROCESSING:
            raise TypeError("The job status '%s' is not 'processing'")
        job.started = datetime.datetime.now(UTC)
        # update retry counter
        job.retryCounter += 1
        try:
            job.output = job(self)
        except m01.remote.exceptions.JobError, error:
            # we skip raising exception on known JobError, log the error and
            # set our error status 
            job.setError(error)
            job.status = interfaces.ERROR
            # log error, we catch them later in our worker
            log.error('processNextJob caused a JobError status -> error!')
            log.exception(error)
        except Exception, error:
            # handle all other Exception
            if job.retryCounter < job.maxRetries:
                # the first 2 times set status back to QUEUED and allow to get
                # picked again based on the previous set retryTime
                job.status = interfaces.QUEUED
                job.setError(error)
                # log and raise error, we catch them later in our worker
                log.error('processNextJob caused an error status -> queued!')
                log.exception(error)
                raise
            else:
                # if we reach maxRetries, we abort and store the last error
                job.setError(error)
                job.status = interfaces.ERROR
                log.error('processNextJob caused an error max retry reached status -> error!')
                log.exception(error)
        else:
            # if no error happens, update status and completed datetime
            job.status = interfaces.COMPLETED
            job.completed = datetime.datetime.now(UTC)
        return True

    # worker start/stop API
    def startProcessor(self):
        """Start processing jobs."""
        if self.isProcessing:
            log.info("Processor '%s' already running" %
                self._jobWorkerThreadName)
            return

        # Start the thread running the processor inside.
        worker = self.jobWorkerFactory(self, **self.jobWorkerArguments)
        thread = threading.Thread(target=worker,
            name=self._jobWorkerThreadName)
        thread.setDaemon(True)
        thread.running = True
        thread.start()
        self.processorStartTime = time.time()
        log.info("Processor '%s' started" % self._jobWorkerThreadName)

    def stopProcessor(self):
        """Stop processing jobs."""
        for thread in threading.enumerate():
            if thread.getName() == self._jobWorkerThreadName:
                thread.running = False
                self.processorStartTime = None
                log.info("Processor '%s' stopped" % self._jobWorkerThreadName)
                break

    @property
    def isProcessing(self):
        """See interfaces.IRemoteProcessor"""
        for thread in threading.enumerate():
            if thread.getName() == self._jobWorkerThreadName:
                if thread.running:
                    return True
                break
        return False

    # scheduler start/stop API
    def startScheduler(self):
        """Start processing scheduling jobs."""
        if self.isScheduling:
            log.info("Scheduler '%s' already running" % 
                self._schedulerWorkerThreadName)
            return

        # Start the thread running the processor inside.
        worker = self.schedulerWorkerFactory(self,
            **self.schedulerWorkerArguments)
        thread = threading.Thread(target=worker,
            name=self._schedulerWorkerThreadName)
        thread.setDaemon(True)
        thread.running = True
        thread.start()
        self.schedulerStartTime = time.time()
        log.info("Scheduler '%s' started" % self._schedulerWorkerThreadName)

    def stopScheduler(self):
        """Stop processing scheduling jobs."""
        for thread in threading.enumerate():
            if thread.getName() == self._schedulerWorkerThreadName:
                thread.running = False
                self.schedulerStartTime = None
                log.info("Scheduler '%s' stopped" %
                    self._schedulerWorkerThreadName)
                break

    @property
    def isScheduling(self):
        """See interfaces.IRemoteProcessor"""
        for thread in threading.enumerate():
            if thread.getName() == self._schedulerWorkerThreadName:
                if thread.running:
                    return True
                break
        return False

    @property
    def _schedulerWorkerThreadName(self):
        """Return name of the processing scheduler thread."""
        # Note: implement another concept if you use more then one remote 
        # processor in one application
        return '%s-%s' % (self.__name__ and self.__name__ or 'root', 'scheduler')

    @property
    def _jobWorkerThreadName(self):
        """Return name of the processing job processing thread."""
        # Note: implement another concept if you use more then one remote 
        # processor in one application
        return '%s-%s' % (self.__name__ and self.__name__ or 'root', 'worker')

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)
