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
"""The most basic source factory that supports all the required interfaces.

This is used for sources that do not require the context.

"""
__docformat__ = "reStructuredText"


import zc.sourcefactory.factories
import zc.sourcefactory.policies

class BasicSourceFactory(zc.sourcefactory.factories.BasicSourceFactory,
                         zc.sourcefactory.policies.BasicSourcePolicy):
    """Basic source factory implementation including a factory and the
    basic policies.

    """
