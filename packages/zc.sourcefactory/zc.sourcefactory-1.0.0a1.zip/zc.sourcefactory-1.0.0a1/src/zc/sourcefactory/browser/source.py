##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
"""
import zope.interface
import zope.component
import zope.browser.interfaces
import zope.publisher.interfaces.browser
import zope.schema.interfaces

import zc.sourcefactory.source


@zope.interface.implementer(zope.browser.interfaces.ITerms)
class FactoredTerms(object):
    """A terms implementation that knows how to handle a source that was
    created through a source factory.
    """

    zope.component.adapts(
        zc.sourcefactory.source.FactoredSource,
        zope.publisher.interfaces.browser.IBrowserRequest)

    def __init__(self, source, request):
        self.source = source
        self.request = request

    def getTerm(self, value):
        title = self.source.factory.getTitle(value)
        token = self.source.factory.getToken(value)
        return self.source.factory.createTerm(
            self.source, value, title, token, self.request)

    def getValue(self, token):
        return self.source.factory.getValue(self.source, token)


class FactoredContextualTerms(FactoredTerms):
    """A terms implementation that knows how to handle a source that was
    created through a contextual source factory.
    """

    zope.component.adapts(
        zc.sourcefactory.source.FactoredContextualSource,
        zope.publisher.interfaces.browser.IBrowserRequest)

    def getTerm(self, value):
        title = self.source.factory.getTitle(self.source.context, value)
        token = self.source.factory.getToken(self.source.context, value)
        return self.source.factory.createTerm(
            self.source.context, self.source, value, title, token,
            self.request)

    def getValue(self, token):
        return self.source.factory.getValue(self.source.context, self.source,
                                            token)


@zope.interface.implementer(zope.schema.interfaces.ITitledTokenizedTerm)
class FactoredTerm(object):
    """A title tokenized term."""

    def __init__(self, value, title, token):
        self.value = value
        self.title = title
        self.token = token
