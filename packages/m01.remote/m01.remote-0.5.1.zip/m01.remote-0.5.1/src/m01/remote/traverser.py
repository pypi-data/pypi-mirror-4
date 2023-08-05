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
"""Traverser
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.publisher.interfaces

import m01.mongo.traverser

import m01.remote.layer
from m01.remote import interfaces


# IRemoteProcessor traverser
class RemoteProcessorTraverser(m01.mongo.traverser.MongoTraverserMixin):
    """A traverser that knows how to look up processor items"""

    zope.component.adapts(interfaces.IRemoteProcessor,
        m01.remote.layer.IRemoteProcessorLayer)

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""
        if name == 'jobFactories':
            return self.context._jobFactories
        if name == 'jobs':
            return self.context._jobs
        if name == 'scheduler':
            return self.context._scheduler

        view = zope.component.queryMultiAdapter((self.context, request), 
            name=name)
        if view is not None:
            return view

        raise zope.publisher.interfaces.NotFound(self.context, name, request)
