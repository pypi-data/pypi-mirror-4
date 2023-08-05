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
"""Testing
$Id:$
"""
__docformat__ = "reStructuredText"

import os
import logging
import time

import zope.component
from zope.schema import ValidationError

import m01.mongo.testing
import m01.mongo.pool
import m01.stub.testing

from m01.remote import job
from m01.remote import exceptions
from m01.remote.processor import RemoteProcessor


###############################################################################
#
# Testing stubs
#
###############################################################################

class EchoJob(job.Job):
    """A simple echo, job implementation."""

    def __call__(self, remoteProcessor):
        return self.input


class SleepJob(job.Job):
    """Sleep job."""

    def __call__(self, remoteProcessor):
        (sleepTime, id) = self.input
        time.sleep(sleepTime)
        log = logging.getLogger('m01.remote')
        log.info('Job: %i' %id)


class ErrorJob(job.Job):
    """A simple error job for testing."""

    def __call__(self, remoteProcessor):
        raise exceptions.JobError('An error occurred.')


class FatalErrorJob(job.Job):
    """A fatal error for testing"""

    def __call__(self, remoteProcessor):
        raise ValidationError('An error occurred.')


testCounter = 0

class TransactionAbortJob(job.Job):
    """A job which counts and calls transaction.abort for testing"""

    def __call__(self, remoteProcessor):
        log = logging.getLogger('m01.remote')
        log.info('Job: %i' % self.input)

        global testCounter
        testCounter += 1

        import transaction
        transaction.abort()


class TestProcessor(RemoteProcessor):
    """RemoteProcessor used for testing hwihc knows our test jobs"""

    def getRemoteProcessorDB(self):
        return m01.mongo.testing.getTestDatabase()

    # job item loader
    def loadRemoteProcessorJobItems(self, data):
        """Load data into the relevant item type"""
        _type = data.get('_type')
        if _type == 'EchoJob':
            obj = EchoJob(data)
        elif _type == 'SleepJob':
            obj = SleepJob(data)
        elif _type == 'ErrorJob':
            obj = ErrorJob(data)
        elif _type == 'FatalErrorJob':
            obj = FatalErrorJob(data)
        elif _type == 'TransactionAbortJob':
            obj = TransactionAbortJob(data)
        else:
            raise TypeError("No class found for mongo _type %s" % _type)
        return obj


###############################################################################
#
# testing setup
#
###############################################################################
from zope.testing.loggingsupport import InstalledHandler


# error message setup
def setUpJobErrorMessageAdapter(test=None):
    zope.component.provideAdapter(exceptions.jobErrorMessageAdapter)


testProcessor  = None

def setUpTestProcessor():
    """Hook up our TestSite instance"""
    global testProcessor
    testProcessor = TestProcessor()
    return testProcessor

def tearDownTestProcessor():
    """Tear down our TestSite instance"""
    global testProcessor
    testProcessor.stopProcessor()
    testProcessor.stopScheduler()
    testProcessor = None

def setUpSchedulerClassTest():
    """Hook up our TestSite instance"""
    m01.mongo.testing.setUpFakeMongoDB()
    global testProcessor
    testProcessor = TestProcessor()
    return testProcessor

def tearDownSchedulerClassTest():
    """Tear down our TestSite instance"""
    global testProcessor
    testProcessor.stopProcessor()
    testProcessor.stopScheduler()
    testProcessor = None
    m01.mongo.testing.tearDownFakeMongoDB()


# stub mongodb server
def setUpMongoDBHook():
    def getMongoDBStubSetUp(test):
        # lazy test setup
        host = 'localhost'
        port = 45030
        here = os.path.dirname(__file__)
        sandBoxDir = os.path.join(here, 'sandbox')
        m01.stub.testing.startMongoDBServer(host, port, sandBoxDir=sandBoxDir,
            sleep=3.0)
        p = m01.mongo.pool.MongoConnectionPool(host, port)
        m01.mongo.testing._testConnection = p.connection
        log_info = InstalledHandler('m01.remote')
        test.globs['log_info'] = log_info
        test.orgJobWorkerArguments = RemoteProcessor.jobWorkerArguments
        test.orgSchedulerWorkerArguments = RemoteProcessor.schedulerWorkerArguments
        RemoteProcessor.jobWorkerArguments = {'waitTime': 0.0}
        RemoteProcessor.schedulerWorkerArguments = {'waitTime': 0.0}
        test.globs['root'] = setUpTestProcessor()
    return getMongoDBStubSetUp

setUpStubMongoDB = setUpMongoDBHook()

def tearDownMongoDBHook():
    def getMongoDBStubTearDown(test):
        tearDownTestProcessor()
        # lazy test tear down
        m01.stub.testing.stopMongoDBServer(sleep=5)
        m01.mongo.testing._testConnection = None
        log_info = test.globs['log_info']
        log_info.clear()
        log_info.uninstall()
        RemoteProcessor.jobWorkerArguments = test.orgJobWorkerArguments
        RemoteProcessor.schedulerWorkerArguments = test.orgSchedulerWorkerArguments
    return getMongoDBStubTearDown

tearDownStubMongoDB = tearDownMongoDBHook()
