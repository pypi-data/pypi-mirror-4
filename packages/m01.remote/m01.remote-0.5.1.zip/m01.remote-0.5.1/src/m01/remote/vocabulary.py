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
"""Vocabularies
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema.interfaces
import zope.schema.vocabulary
from zope.security.proxy import removeSecurityProxy

import z3c.form.interfaces
import z3c.form.term

from m01.remote import interfaces


class JobNameTerms(z3c.form.term.Terms):
    """Job name terms. It's really great what we can do with z3c.form"""

    zope.component.adapts(
        zope.interface.Interface,
        z3c.form.interfaces.IFormLayer,
        interfaces.IJobNameTermsAware,
        zope.schema.interfaces.ITextLine,
        z3c.form.interfaces.IWidget)

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        # setup a list of job.__name__ as vocabulary terms
        context = removeSecurityProxy(context)
        if interfaces.ISchedulerItem.providedBy(context):
            remoteProcessor = context.__parent__.__parent__
        elif interfaces.IScheduler.providedBy(context):
            remoteProcessor = context.__parent__
        else:
            remoteProcessor = context
        terms = [zope.schema.vocabulary.SimpleTerm(name, name, name)
                 for name in remoteProcessor._jobFactories.keys()]
        self.terms = zope.schema.vocabulary.SimpleVocabulary(terms)
