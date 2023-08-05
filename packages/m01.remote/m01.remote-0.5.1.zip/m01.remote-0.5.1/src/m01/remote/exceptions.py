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
"""Exceptions
$Id:$
"""
__docformat__ = "reStructuredText"

import datetime
import zope.interface
import zope.component

from m01.mongo import UTC
from m01.remote import interfaces


class JobError(Exception):
    """An error occurred while executing the job, abort now."""
    pass


@zope.component.adapter(interfaces.IJob, zope.interface.Interface)
@zope.interface.implementer(interfaces.IJobErrorMessage)
def jobErrorMessageAdapter(job, error):
    """Returns a message for the given error
    
    Implement you own adapters for (job, error) and provide a better error
    message
    """
    dt = datetime.datetime.now(UTC)
    return '[%s] %s' % (dt.isoformat(), str(error))
