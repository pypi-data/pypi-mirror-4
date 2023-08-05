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
"""Scheduling start subscriber
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.lifecycleevent.interfaces

from m01.remote import interfaces


@zope.component.adapter(interfaces.ISchedulerItem,
                        zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def objectModifiedSubscriber(item, event):
    """Event subscriber for re-schedule ISchedulerItem."""
    item.__parent__.reScheduleItem(item)
