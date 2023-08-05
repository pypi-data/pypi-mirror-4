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
"""Tests
$Id:$
"""
__docformat__ = "reStructuredText"

import doctest
import unittest

import z3c.testing
import m01.mongo.testing

from m01.remote import interfaces
from m01.remote import processor
from m01.remote import scheduler
from m01.remote import worker
from m01.remote import testing


class RemoteProcessorTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IRemoteProcessor

    def getTestClass(self):
        return processor.RemoteProcessor


class SchedulerWorkerTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISchedulerWorker

    def getTestClass(self):
        return worker.SchedulerWorker

    def getTestPos(self):
        return (None, None)


class SimpleJobWorkerTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISimpleJobWorker

    def getTestClass(self):
        return worker.SimpleJobWorker

    def getTestPos(self):
        return (None, None)


class MultiJobWorkerTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IMultiJobWorker

    def getTestClass(self):
        return worker.MultiJobWorker

    def getTestPos(self):
        return (None, None)


class SchedulerTest(m01.mongo.testing.MongoStorageBaseTest):

    def setUp(self):
        testing.setUpSchedulerClassTest()
        super(SchedulerTest, self).setUp()

    def tearDown(self):
        testing.tearDownSchedulerClassTest()
        super(SchedulerTest, self).tearDown()

    def getTestInterface(self):
        return interfaces.IScheduler

    def getTestClass(self):
        return scheduler.Scheduler

    def getTestData(self):
        return testing.testProcessor


class CronTest(m01.mongo.testing.MongoItemBaseTest):

    def getTestInterface(self):
        return interfaces.ICron

    def getTestClass(self):
        return scheduler.Cron

    def getTestData(self):
        return {'jobName': u'foo', 'active': True}


class DelayTest(m01.mongo.testing.MongoItemBaseTest):

    def getTestInterface(self):
        return interfaces.IDelay

    def getTestClass(self):
        return scheduler.Delay

    def getTestData(self):
        return {'jobName': u'foo', 'active': True, 'delay': 42, 'retryDelay': 42}


class EchoJobTest(m01.mongo.testing.MongoItemBaseTest):

    def getTestInterface(self):
        return interfaces.IJob

    def getTestClass(self):
        return testing.EchoJob

    def getTestData(self):
        return {'__name__': u'job'}


class ErrorJobTest(m01.mongo.testing.MongoItemBaseTest):

    def getTestInterface(self):
        return interfaces.IJob

    def getTestClass(self):
        return testing.ErrorJob

    def getTestData(self):
        return {'__name__': u'job'}


class SleepJobTest(m01.mongo.testing.MongoItemBaseTest):

    def getTestInterface(self):
        return interfaces.IJob

    def getTestClass(self):
        return testing.SleepJob

    def getTestData(self):
        return {'__name__': u'job'}


def test_suite():
    suites = []
    append = suites.append
    # real mongo database tests using our mongodb stub
    testNames = ['worker.txt',
                 'scheduler.txt',
                 'README.txt']
    for name in testNames:
        append(
            doctest.DocFileSuite(name,
                setUp=testing.setUpStubMongoDB,
                tearDown=testing.tearDownStubMongoDB,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        )
    append(unittest.makeSuite(RemoteProcessorTest))
    append(unittest.makeSuite(SchedulerWorkerTest))
    append(unittest.makeSuite(SimpleJobWorkerTest))
    append(unittest.makeSuite(MultiJobWorkerTest))
    append(unittest.makeSuite(SchedulerTest))
    append(unittest.makeSuite(CronTest))
    append(unittest.makeSuite(DelayTest))
    append(unittest.makeSuite(EchoJobTest))
    append(unittest.makeSuite(ErrorJobTest))
    append(unittest.makeSuite(SleepJobTest))
    return unittest.TestSuite(suites)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
