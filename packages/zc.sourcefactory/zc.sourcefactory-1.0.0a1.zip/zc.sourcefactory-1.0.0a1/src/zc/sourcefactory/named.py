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
"""Named source binder

"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema.interfaces

import zc.sourcefactory.interfaces


@zope.interface.implementer(zope.schema.interfaces.IContextSourceBinder)
class NamedSource(object):
    """Factory for named sources.

    This is a generic thin wrapper to look up sources by name.
    """

    def __init__(self, name):
        self.name = name

    def __call__(self, context):
        factory = zope.component.getUtility(
            zc.sourcefactory.interfaces.INamedSource, name=self.name)
        source = factory()
        if zope.schema.interfaces.IContextSourceBinder.providedBy(source):
            source = source(context)
        return source
