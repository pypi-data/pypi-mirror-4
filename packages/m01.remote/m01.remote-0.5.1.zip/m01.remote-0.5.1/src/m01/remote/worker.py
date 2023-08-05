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
"""Remote processor worker
$Id:$
"""
__docformat__ = "reStructuredText"

import logging
import threading
import time

import transaction
import zope.interface

from m01.remote import interfaces

log = logging.getLogger('m01.remote')

THREAD_STARTUP_WAIT = 0.05


class SchedulerWorker(object):
    """Worker which is scheduling new jobs"""

    zope.interface.implements(interfaces.ISchedulerWorker)

    def __init__(self, remoteProcessor, waitTime=1.0):
        self.remoteProcessor = remoteProcessor
        self.waitTime = waitTime

    @property
    def running(self):
        th = threading.currentThread()
        if hasattr(th, 'running'):
            return th.running
        log.error('SchedulerWorker: no currentThread')
        # fallback for InterfaceBaseTest
        return False

    def doScheduleNextJob(self):
        try:
            # returns True or False
            return self.remoteProcessor.scheduleNextJob()
        except Exception, error:
            # This thread should never crash, thus a blank except
            log.error('SchedulerWorker: caused an error!')
            log.exception(error)
            # return True and force to call commit and try again
            return True

    def __call__(self):
        """Run till we have no item for scheduling"""
        while self.running:
            jobid = self.doScheduleNextJob()
            # If there are no jobs available, sleep a little bit and then
            # check again.
            if jobid:
                # commit processed job
                transaction.commit()
            else:
                time.sleep(self.waitTime)


class SimpleJobWorker(object):
    """Worker which is processing jobs in a single thread"""

    zope.interface.implements(interfaces.ISimpleJobWorker)

    def __init__(self, remoteProcessor, *args, **kwargs):
        self.remoteProcessor = remoteProcessor
        self.jobQuery = kwargs.pop('jobQuery', None)
        self.waitTime = kwargs.pop('waitTime', 0.5)

    @property
    def running(self):
        th = threading.currentThread()
        if hasattr(th, 'running'):
            return th.running
        log.error('SimpleJobWorker: no currentThread')
        return False

    def doProcessNextJob(self):
        """Process next job without to commit transaction"""
        try:
            # return the next job or False
            return self.remoteProcessor.processNextJob(self.jobQuery)
        except Exception, error:
            # This thread should never crash, thus a blank except
            log.error('SimpleJobWorker caused an error!')
            log.exception(error)
            # return True and force to call commit and try again
            return True

    def __call__(self):
        """Run till we have no jobs for processing"""
        while self.running:
            result = self.doProcessNextJob()
            # commit processed job or new retryTime now
            transaction.commit()
            if not result:
                # If there are no jobs available, sleep a little bit and then
                # check again.
                time.sleep(self.waitTime)


class MultiJobWorker(object):
    """Worker which processes more the one job at the same time using threads"""

    zope.interface.implements(interfaces.IMultiJobWorker)


    def __init__(self, remoteProcessor, *args, **kwargs):
        self.remoteProcessor = remoteProcessor
        self.jobQuery = kwargs.pop('jobQuery', None)
        self.waitTime = kwargs.pop('waitTime', 0.5)
        self.maxThreads = kwargs.pop('maxThreads', 5)
        self.threads = []

    @property
    def running(self):
        th = threading.currentThread()
        if hasattr(th, 'running'):
            return th.running
        log.error('MultiJobWorker: no currentThread')
        return False

    def doPullNextJob(self):
        """Returns the next job for processing"""
        return self.remoteProcessor.pullNextJob(self.jobQuery)

    def doProcessJob(self, jobid):
        """Get job by id, process, commit transaction"""
        try:
            # process the next job and commit
            self.remoteProcessor.processJob(jobid)
        except Exception, error:
            # This thread should never crash, thus a blank except
            log.error('JobWorker caused an error!')
            log.exception(error)
        finally:
            # commit job processing or error
            transaction.commit()

    def __call__(self):
        # Start the processing loop
        while self.running:
            # remove dead threads
            for thread in self.threads:
                if not thread.isAlive():
                    self.threads.remove(thread)
            # respect maximum threads
            if len(self.threads) == self.maxThreads:
                time.sleep(self.waitTime)
                continue
            # try to get a new job
            job = self.doPullNextJob()
            if job is None:
                # if we didn't find a new job wait and continue
                time.sleep(self.waitTime)
                continue
            else:
                # process the new job in a new thread. Since we use a new
                # thread, the new thread has to catch the job by it's id
                jobid = job.__name__
                log.info('MultiJobWorker: processing job %s' % jobid)
                thread = threading.Thread(
                    target=self.doProcessJob, args=(jobid,))
                self.threads.append(thread)
                thread.start()
                # Give the thread some time to start up:
                time.sleep(THREAD_STARTUP_WAIT)
