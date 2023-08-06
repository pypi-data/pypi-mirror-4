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
"""Basic factories.

"""
__docformat__ = "reStructuredText"


import zope.interface
import zope.schema.interfaces

import zc.sourcefactory.interfaces
import zc.sourcefactory.source


@zope.interface.implementer(zc.sourcefactory.interfaces.ISourceFactory)
class BasicSourceFactory(object):
    """Abstract base class for a source factory.

    Implementors must provide an implementation for `getValues`.
    """

    source_class = zc.sourcefactory.source.FactoredSource

    def __new__(cls, *args, **kw):
        """Create the factory object and return source."""
        factory = object.__new__(cls)
        factory.__init__(*args, **kw)
        return cls.source_class(factory)


class ContextualSourceFactory(BasicSourceFactory):
    """Abstract base class for a source factory for a context-bound source.

    Implementors must provide an implementation for `getValues`.
    """

    source_class = zc.sourcefactory.source.FactoredContextualSource

    def __new__(cls, *args, **kw):
        """Create the factory object and return source."""
        factory = object.__new__(cls)
        factory.__init__(*args, **kw)
        return FactoredContextualSourceBinder(factory, cls.source_class)


@zope.interface.implementer(zope.schema.interfaces.IContextSourceBinder)
class FactoredContextualSourceBinder(object):
    """A context source binder for factored sources."""

    def __init__(self, factory, source_class):
        self.factory = factory
        self.source_class = source_class

    def __call__(self, context, *args, **kwargs):
        return self.source_class(self.factory, context, *args, **kwargs)
