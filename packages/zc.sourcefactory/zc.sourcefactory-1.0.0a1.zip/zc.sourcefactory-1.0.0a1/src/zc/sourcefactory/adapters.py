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
"""Support to adapt factored sources to some common interfaces.

"""
__docformat__ = "reStructuredText"

import zope.schema.interfaces
import zope.component
import zc.sourcefactory.source

@zope.interface.implementer(zope.schema.interfaces.ISourceQueriables)
@zope.component.adapter(zc.sourcefactory.source.FactoredSource)
def getSourceQueriables(factored_source):
    return zope.component.queryMultiAdapter(
        (factored_source, factored_source.factory),
        zope.schema.interfaces.ISourceQueriables)
