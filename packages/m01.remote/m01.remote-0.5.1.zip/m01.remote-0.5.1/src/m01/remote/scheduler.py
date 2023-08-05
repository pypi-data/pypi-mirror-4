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
"""Scheduler
$Id:$
"""
__docformat__ = "reStructuredText"

import logging
import datetime
import thread

import pymongo.errors

import zope.interface

import m01.mongo.storage
import m01.mongo.item
from m01.mongo import UTC
from m01.mongo.fieldproperty import MongoFieldProperty

from m01.remote import interfaces

log = logging.getLogger('m01.remote')


_marker = object()


# datetime based operators
incSeconds = lambda dt: dt + datetime.timedelta(seconds=1)
incMinutes = lambda dt: dt + datetime.timedelta(seconds=60)
incHours = lambda dt: dt + datetime.timedelta(seconds=60*60)
incDays = lambda dt: dt + datetime.timedelta(days=1)
def incMonth(dt):
    data = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    m = dt.month -1
    if m == 1:
        # see if we have a leap year
        y = dt.year
        if y % 4 != 0:
            days = 28
        elif y % 400 == 0:
            days = 29
        elif y % 100 == 0:
            days = 28
        else:
            days = 29
    else:
        days = data[m]
    return dt + datetime.timedelta(days=days)


def adjustCallTime(cron, dt):
    """Reset call time for the smaller unit then we have values for"""
    # start with smaller unit and skip others
    if cron.minute:
        dt = dt.replace(second=0)
    elif cron.hour:
        dt = dt.replace(minute=0)
    elif cron.dayOfMonth:
        dt = dt.replace(hour=0)
    elif cron.dayOfWeek:
        dt = dt.replace(hour=0)
    elif cron.month:
        dt = dt.replace(day=1)
    return dt


class SchedulerMixin(object):
    """Scheduler mixin class"""

    def reScheduleItem(self, item, callTime=None):
        """Reschedule item based on transaction commit handling"""
        if callTime is None:
            callTime = datetime.datetime.now(UTC)
        # calculate next call time, but first make sure we reset nextCallTime
        item.nextCallTime = None
        item.getNextCallTime(callTime)

    def reScheduleItems(self, callTime=None):
        """Reschedule all items based on transaction commit handling"""
        if callTime is None:
            callTime = datetime.datetime.now(UTC)
        for item in self.values():
            self.reScheduleItem(item, callTime)

    def getNextCachedItem(self, callTime=None):
        if callTime is None:
            callTime = datetime.datetime.now(UTC)
        for item in self._cache_added.values():
            retryTime = self.updateRetryTime(item.dump(), callTime)
            if retryTime:
                item.retryTime = retryTime
                return item

    def updateRetryTime(self, data, callTime=None):
        if callTime is None:
            callTime = datetime.datetime.now(UTC)
        _id = data['_id']
        __name__ = data['__name__']
        nextCallTime = data.get('nextCallTime')
        oldRetryTime = data.get('retryTime')
        retryTime = oldRetryTime
        if retryTime is None:
            retryTime = callTime

        # check some conditions before we update the current retryTime
        if __name__ in self._cache_removed:
            return False
        if not data.get('active'):
            # not active item
            return False
        if nextCallTime > callTime:
            # not scheduled for yet
            return False

        # check retryTime
        if retryTime <= callTime:
            retryDelay = data.get('retryDelay', 300)
            newTime = callTime + datetime.timedelta(seconds=retryDelay)
            # important, mongodb will round datetime to milisecond, so we have 
            # to round too
            newTime = newTime.replace(microsecond=newTime.microsecond/1000*1000)
            # set new retryTime based on old retryTime, this will fail if
            # another processor was updating the retryTime befor we could
            self.collection.update({'_id': _id,
                                    'active': True,
                                    'retryTime': oldRetryTime},
                                   {'$set': {'retryTime': newTime}},
                                   save=True)
            # check if we had sucessfully set our new retryTime
            data = self.collection.find_one({'_id': _id, 'active': True})
            if data is None:
                # this must be a new not commited item, that's fine
                return newTime
            elif data.get('retryTime') is not None and \
                data.get('retryTime') == newTime:
                # our update was sucessfull
                return newTime
            else:
                # another process updated the retryTime
                return False

        return False

    def pullNextSchedulerItem(self, callTime=None):
        """Pull next item"""
        if callTime is None:
            callTime = datetime.datetime.now(UTC)
        # get one item with lower callTime and lower retryTime
        # first check our cache
        item = self.getNextCachedItem(callTime)
        if item is None:
            # now check mongodb
            try:
                spec = {'active': True,
                        'nextCallTime': {'$lt':callTime}}
                data = self.doFindOne(self.collection, spec)
                if data is not None:
                    retryTime = self.updateRetryTime(data, callTime)
                    if retryTime:
                        try:
                            # add new retry time
                            data['retryTime'] = retryTime
                            # load, locate and cache if not cached
                            item = self.doLoad(data)
                            # update nextCallTime which will reschedule for
                            # next call
                            item.getNextCallTime(callTime)
                            # join transaction handling
                            self.ensureTransaction()
                        except (KeyError, TypeError), e:
                            log.error('pullNextSchedulerItem caused an error!')
                            log.exception(e)
            except (TypeError, pymongo.errors.ConnectionFailure,
                pymongo.errors.AutoReconnect, pymongo.errors.InvalidName), e:
                log.error('pullNextSchedulerItem caused an error!')
                log.exception(e)
        
        # return item
        return item


class Scheduler(SchedulerMixin, m01.mongo.storage.MongoStorage):
    """Scheduler storage.
    
    The really important part in this concept is, that we prevent calling an
    item more then once if more then one RemoteProcessor is running using the
    same mongodb as item storage
    
    First we us a pending marker which prevents to recalculate the nextCallTime
    for pending items.
    
    We mark pending items as picked with the picked datetime which should
    prevent to get items twice till the nextCallTime is smaller then the 
    current datetime.
    
    Note: you can use this class as the first inherited class and the 
    RemoteProcessor class as the second inherited class if you like to
    implement a remote processor where it's items are scheduler items.
    Note: inherit the other way arround will run into recursion erros because
    the methods reScheduleItems and reScheduleItem from the remote processor
    class is calling the scheduler methods with the same name:
    
    class MyProcessorWithCronOrDelayItems(m01.remote.scheduler.Scheduler,
        m01.remote.processor.RemoteProcessor):
        "My processor with scheduler items as items"

    """

    zope.interface.implements(interfaces.IScheduler)

    __name__ = u'scheduler'

    def __init__(self, parent):
        # do not call super class which whould override our __name__
        # initialize __parent__
        self.__parent__ = parent

    @property
    def collection(self):
        """Returns a thread local shared collection for scheduler items."""
        return self.__parent__.getRemoteProcessorSchedulerCollection()

    @property
    def cacheKey(self):
        return 'm01.remote.scheduler.%s.%i' % (id(self), thread.get_ident())

    def load(self, data):
        """Load data into the relevant item type
        
        Note: define additional scheduler items if you add custom scheduler
        items.
        """
        _type = data.get('_type')
        if _type == 'Cron':
            obj = Cron(data)
        elif _type == 'Delay':
            obj = Delay(data)
        else:
            raise TypeError("No class found for mongo _type %s" % _type)
        obj.__parent__ = self
        obj._m_changed = False
        return obj

    def remove(self, item):
        super(Scheduler, self).__delitem__(item.__name__)

    def getBatchData(self, query=None, page=1, size=25, sortName=None,
        sortOrder=None, searchText=None, fields=None, skipFilter=False):
        # revert sort order, newest first if nothing else is given
        if sortName is None:
            sortName = 'title'
        if sortOrder is None:
            sortOrder = 1
        return super(Scheduler, self).getBatchData(query, page, size,
            sortName, sortOrder, searchText, fields, skipFilter)


class SchedulerItemBase(m01.mongo.item.MongoStorageItem):
    """Scheduler item base inclduing nextCallTime handling"""

    jobName = MongoFieldProperty(interfaces.ISchedulerItem['jobName'])
    title = MongoFieldProperty(interfaces.ISchedulerItem['title'])
    description = MongoFieldProperty(interfaces.ISchedulerItem['description'])
    input = MongoFieldProperty(interfaces.ISchedulerItem['input'])
    active = MongoFieldProperty(interfaces.ISchedulerItem['active'])
    nextCallTime = MongoFieldProperty(interfaces.ISchedulerItem['nextCallTime'])
    retryTime = MongoFieldProperty(interfaces.ISchedulerItem['retryTime'])
    retryDelay = MongoFieldProperty(interfaces.ISchedulerItem['retryDelay'])

    def __init__(self, data):
        # first set nextCallTime
        super(SchedulerItemBase, self).__init__(data)
        # after all arguments get set, we can calculate our nextCallTime
        if not self.nextCallTime:
            callTime = datetime.datetime.now(UTC)
            self.nextCallTime = self.getNextCallTime(callTime)
        # after set nextCallTime, mark a s not changed
        self._m_changed = None


class Cron(SchedulerItemBase):
    """A cron scheduler item."""

    zope.interface.implements(interfaces.ICron)

    minute = MongoFieldProperty(interfaces.ICron['minute'])
    hour = MongoFieldProperty(interfaces.ICron['hour'])
    dayOfMonth = MongoFieldProperty(interfaces.ICron['dayOfMonth'])
    month = MongoFieldProperty(interfaces.ICron['month'])
    dayOfWeek = MongoFieldProperty(interfaces.ICron['dayOfWeek'])

    _dumpNames = ['_id', '_type', '_version', '__name__',
                  'created', 'modified'
                  'title', 'description',
                  'jobName', 'input', 'active',
                  'nextCallTime', 'retryTime', 'retryDelay',
                  'minute', 'hour', 'dayOfMonth', 'month', 'dayOfWeek',
                 ]

    def getNextCallTime(self, callTime):
        """Return next call time.

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
        if self.active:
            currentNextCallTime = self.nextCallTime
            if not self.nextCallTime or self.nextCallTime <= callTime:
                next = adjustCallTime(self, callTime)
    
                # setup increase methods
                inc = incSeconds
                if self.minute and len(self.minute):
                    # increase in minutes for catch first minute
                    inc = incMinutes
                elif self.hour and len(self.hour):
                    # increase in hours for catch first hour
                    inc = incHours
                elif self.hour and len(self.hour):
                    # increase in days for catch first day of month
                    inc = incDays
                elif self.dayOfWeek and len(self.dayOfWeek):
                    # increase in days for catch first day of week
                    inc = incDays
                elif self.month and len(self.month):
                    # increase in month for catch first month
                    inc = incMonth
    
                while next <= callTime+ datetime.timedelta(days=365):
                    next = inc(next)
                    fields = next.timetuple()
                    # setup default values for each field
                    minute = self.minute or range(60)
                    hour = self.hour or range(24)
                    month = self.month or range(1, 13)
                    dayOfWeek = self.dayOfWeek or range(7)
                    dayOfMonth = self.dayOfMonth or range(1, 32)
                    if ((fields[1] in month) and
                        (fields[2] in dayOfMonth) and
                        (fields[3] in hour) and
                        (fields[4] in minute) and
                        (fields[6] % 7 in dayOfWeek)):
                        # set next call time
                        self.nextCallTime = next
                        break
                # return previous next call time
                return currentNextCallTime
        else:
            # set explicit to None as long as not active
            self.nextCallTime = None
        return self.nextCallTime

    def __repr__(self):
        return '<%s %s for: %r>' %(self.__class__.__name__, self.__name__,
            self.jobName)


class Delay(SchedulerItemBase):
    """A delay definition for scheduled jobs."""
    zope.interface.implements(interfaces.IDelay)

    delay = MongoFieldProperty(interfaces.IDelay['delay'])

    _dumpNames = ['_id', '_type', '_version', '__name__',
                  'created', 'modified',
                  'title', 'description',
                  'jobName', 'input', 'active',
                  'nextCallTime', 'retryTime', 'retryDelay',
                  'delay',
                 ]

    def getNextCallTime(self, callTime):
        if self.active and self.delay:
            nextTime = self.nextCallTime
            if not nextTime or self.nextCallTime <= callTime:
                # callculate the next call time and cache it
                # set the new next call time
                newTime = callTime + datetime.timedelta(seconds=self.delay)
                self.nextCallTime = newTime
                # if initial nextCallTime was 0 (zero) return new calculated
                # next call time.
                return nextTime and nextTime or newTime
        else:
            # set explicit to None as long as not active an no delay is set
            self.nextCallTime = None
        return self.nextCallTime

    def __repr__(self):
        return '<%s %s for: %r>' %(self.__class__.__name__, self.__name__,
            self.jobName)
