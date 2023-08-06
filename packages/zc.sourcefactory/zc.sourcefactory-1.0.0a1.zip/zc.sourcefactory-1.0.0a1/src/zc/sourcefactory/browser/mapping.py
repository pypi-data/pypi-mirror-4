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
"""Mapping-source related terms stuff
"""
import zope.proxy
import zope.interface
import zope.component
import zope.browser
import zope.publisher.interfaces.browser

import zc.sourcefactory.mapping


@zope.interface.implementer(zope.browser.interfaces.ITerms)
class MappedTerms(object):
    """A terms implementation that knows how to handle a source that was 
    created through a source factory.
    """

    zope.component.adapts(zc.sourcefactory.mapping.ValueMappingSource,
        zope.publisher.interfaces.browser.IBrowserRequest)

    def __init__(self, source, request):
        self.base = zope.component.getMultiAdapter(
            [source.base, request], zope.browser.interfaces.ITerms)
        self.source = source
        self.request = request

    def getTerm(self, value):
        real_value = self.source.mapReverse(value)
        term = self.base.getTerm(real_value)
        return MappedTermProxy(value, term)

    def getValue(self, token):
        return self.source.map(self.base.getValue(token))


class MappedTermProxy(zope.proxy.ProxyBase):
    """A mapped term that provides access to the mapped value
    without destroying the real term.

    """

    __slots__ = ('value',)

    def __new__(self, value, baseterm):
        return zope.proxy.ProxyBase.__new__(self, baseterm)

    def __init__(self, value, baseterm):
        zope.proxy.ProxyBase.__init__(self, baseterm)
        self.value = value
