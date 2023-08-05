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
"""Remote jobs
$Id:$
"""
__docformat__ = "reStructuredText"

import logging
import thread
import datetime

import bson.objectid
import pymongo.errors

import zope.interface

import m01.mongo.item
import m01.mongo.container
from m01.mongo import UTC
from m01.mongo.fieldproperty import MongoFieldProperty

import m01.remote.exceptions
from m01.remote import interfaces

log = logging.getLogger('m01.remote')


class JobFactories(m01.mongo.container.MongoContainer):
    """Stores job factories"""

    zope.interface.implements(interfaces.IJobFactories)

    __name__ = u'jobFactories'

    def __init__(self, parent):
        self.__parent__ = parent

    @property
    def collection(self):
        """Returns a thread local shared collection for jobs."""
        return self.__parent__.getRemoteProcessorJobFactoryCollection()

    @property
    def cacheKey(self):
        return 'm01.remote.factories.%s.%i' % (id(self), thread.get_ident())

    def load(self, data):
        """Load data into the relevant item type"""
        obj = self.__parent__.loadRemoteProcessorJobItems(data)
        obj.__parent__ = self
        obj._m_changed = False
        return obj

    def getBatchData(self, query=None, page=1, size=25, sortName=None,
        sortOrder=None, searchText=None, fields=None, skipFilter=False):
        # revert sort order, newest first if nothing else is given
        if sortName is None:
            sortName = '__name__'
        if sortOrder is None:
            sortOrder = 1
        return super(JobFactories, self).getBatchData(query, page, size,
            sortName, sortOrder, searchText, fields, skipFilter)


def sortQueued(item1, item2):
    # sor tby queued datetime
    v1 = getattr(item1, 'queued', u'x')
    v2 = getattr(item2, 'queued', u'x')
    return cmp(v1, v2)

class Jobs(m01.mongo.container.MongoContainer):
    """Stores processing jobs"""

    zope.interface.implements(interfaces.IJobs)

    __name__ = u'jobs'

    def __init__(self, parent):
        self.__parent__ = parent

    @property
    def collection(self):
        """Returns a thread local shared collection for job factories."""
        return self.__parent__.getRemoteProcessorJobCollection()

    @property
    def cacheKey(self):
        return 'm01.remote.jobs.%s.%i' % (id(self), thread.get_ident())

    def load(self, data):
        """Load data into the relevant item type"""
        obj = self.__parent__.loadRemoteProcessorJobItems(data)
        obj.__parent__ = self
        obj._m_changed = False
        return obj

    def add(self, job):
        """Add a job with it's given __name__"""
        assert job.__name__ is not None
        self[job.__name__] = job

    def updateRetryTime(self, data, callTime=None):
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
        # preconditions
        # check some conditions before we update the current retryTime
        if data['__name__'] in self._cache_removed:
            return None
        if data.get('status') != interfaces.QUEUED:
            return None
        if not data.get('active'):
            # not active item
            return None

        # keep the old retry time for later
        oldRetryTime = data.get('retryTime')
        retryTime = oldRetryTime
        if retryTime is None:
            retryTime = callTime

        # get a callTime if None is given
        if callTime is None:
            callTime = datetime.datetime.now(UTC)

        # check retryTime
        if retryTime <= callTime:
            _id = data['_id']
            retryDelay = data.get('retryDelay', 300)
            newTime = callTime + datetime.timedelta(seconds=retryDelay)
            # important, mongodb will round datetime to milisecond, so we have 
            # to round too
            newTime = newTime.replace(microsecond=newTime.microsecond/1000*1000)
            # set new retryTime based on old retryTime, this will fail if
            # another processor was updating the retryTime befor we do
            self.collection.update({'_id': _id,
                                    'active': True,
                                    'retryTime': oldRetryTime},
                                   {'$set': {'retryTime': newTime,
                                             'status': interfaces.PROCESSING}})
            # check if we had sucessfully set our new retryTime
            orgData = data
            data = self.collection.find_one({'_id': _id, 'active': True})
            if data is None:
                # this must be a new not commited item, that's fine
                orgData['retryTime'] = newTime
                orgData['status'] = interfaces.PROCESSING
                return orgData
            elif data['retryTime'] == newTime:
                # our update was sucessfull
                return data
            else:
                # another process updated the retryTime
                return None

        return None

    def getNextQueuedItem(self, jobQuery=None, callTime=None):
        """Get the next queued item"""
        # setup optional attrs if not given
        spec = {'active': True, 'status': interfaces.QUEUED}
        if jobQuery is not None:
            # spec allways overrides the jobQuery, this prevents to override
            # the active and status values
            jobQuery.update(spec)
            spec = jobQuery
        if callTime is None:
            callTime = datetime.datetime.now(UTC)
        try:
            # iterate queued jobs
            for data in self.collection.find(spec).sort('queued', 1):
                # check if the retry time will fit and lock the item
                data = self.updateRetryTime(data, callTime)
                if data is not None:
                    try:
                        # load, locate and cache
                        job = self.doLoad(data)
                        # join transaction handling
                        self.ensureTransaction()
                        return job
                    except (KeyError, TypeError), e:
                        log.error('getNextQueuedItem caused an error!')
                        log.exception(e)
        except (TypeError, pymongo.errors.ConnectionFailure,
                pymongo.errors.AutoReconnect, pymongo.errors.InvalidName), e:
            log.error('getNextQueuedItem caused an error!')
            log.exception(e)

    def pullNextJob(self, jobQuery=None, callTime=None):
        """Pull next job"""
        retryTime = None
        if callTime is None:
            callTime = datetime.datetime.now(UTC)
        # get the next queued item
        job = self.getNextQueuedItem(jobQuery, callTime)
        if job is not None:
            # update job status and set picked datetime
            job.status = interfaces.PROCESSING
            job.picked = datetime.datetime.now(UTC)
        # return job
        return job

    def getBatchData(self, query=None, page=1, size=25, sortName=None,
        sortOrder=None, searchText=None, fields=None, skipFilter=False):
        # revert sort order, newest first if nothing else is given
        if sortName is None:
            sortName = 'created'
        if sortOrder is None:
            sortOrder = -1
        return super(Jobs, self).getBatchData(query, page, size, sortName,
            sortOrder, searchText, fields, skipFilter)


class Job(m01.mongo.item.MongoContainerItem):
    """Job base class."""

    zope.interface.implements(interfaces.IJob)

    # only simple mongodb data are allowed, implement your own concept if you
    # need more specific input or output values
    input = None
    output = None

    jobName = MongoFieldProperty(interfaces.IJob['jobName'])
    active = MongoFieldProperty(interfaces.IJob['active'])
    retryTime = MongoFieldProperty(interfaces.IJob['retryTime'])
    retryDelay = MongoFieldProperty(interfaces.IJob['retryDelay']) 
    status = MongoFieldProperty(interfaces.IJob['status'])
    retryCounter = MongoFieldProperty(interfaces.IJob['retryCounter'])
    maxRetries = MongoFieldProperty(interfaces.IJob['maxRetries'])
    errors = MongoFieldProperty(interfaces.IJob['errors'])
    created = MongoFieldProperty(interfaces.IJob['created'])
    queued = MongoFieldProperty(interfaces.IJob['queued'])
    picked = MongoFieldProperty(interfaces.IJob['picked'])
    started = MongoFieldProperty(interfaces.IJob['started'])
    completed = MongoFieldProperty(interfaces.IJob['completed'])

    _skipNames = []
    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified',
                  'type', 'jobName', 'active', 'retryTime', 'retryDelay',
                  'status', 'retryCounter', 'maxRetries',
                  'input', 'output', 'errors',
                  'queued', 'picked', 'started', 'completed',
                 ]

    def __init__(self, data=None):
        if data is None:
            data = {}
        super(Job, self).__init__(data)

    def setError(self, error):
        """Appends errors to the error list using IJobErrorMessage"""
        msg = zope.component.getMultiAdapter((self, error),
            interfaces.IJobErrorMessage)
        self.errors.append(unicode(msg))

    def applyInputData(self, data, input=None):
        # override a default input if given or use default
        # change this in our implementation if you need another concept
        if input is None:
            input = self.input
        data['input'] = input

    def getJob(self, input=None):
        """Clone the original job, apply input, new _id and relevant data"""
        data = self.dump()
        # remove __parent__
        if '__parent__' in data:
            del data['__parent__']
        # apply new mongo id
        _id = bson.objectid.ObjectId()
        data['_id'] = _id
        # now the job provides an ObjectID as __name__
        data['__name__'] = unicode(_id)
        # apply the org job __name__ as jobName
        data['jobName'] = self.__name__
        # reset _version
        data['_version'] = 0
        # adjust date
        now = datetime.datetime.now(UTC)
        data['created'] = now
        data['modified'] = now
        self.applyInputData(data, input)
        job = self.__class__(data)
        job._m_changed = True
        return job

    def __call__(self, remoteProcessor):
        """Process a job."""
        if self.status == interfaces.PROCESSING:
            raise m01.remote.exceptions.JobError(
                "Can't process a job without the status PROCESSING")
        # implement here what your job should do and raise JobError which will
        # get logged in our job processing log if something bad happens!
        # NOTE: any JobError will abort processing any other error forces to 
        # retry till the maxRetries get reached

    def __repr__(self):
        if self.jobName is not None:
            return '<%s %r %s>' % (self.__class__.__name__, self.jobName,
                self.__name__)
        else:
            return '<%s %r>' % (self.__class__.__name__, self.__name__)
