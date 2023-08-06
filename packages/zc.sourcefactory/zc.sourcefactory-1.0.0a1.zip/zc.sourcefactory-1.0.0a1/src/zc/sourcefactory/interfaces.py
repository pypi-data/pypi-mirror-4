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
"""Interfaces for zc.sourcefactory.

"""
__docformat__ = "reStructuredText"


import zope.interface
import zope.schema.interfaces

class ISourceFactory(zope.interface.Interface):

    def __call__():
        """Create and return the source or source binder."""


class IFactoredSource(zope.schema.interfaces.IIterableSource):
    """An iterable source that was created from a source factory."""

    factory = zope.interface.Attribute("The source factory.")


class IContextualSource(IFactoredSource):
    """A source operating in context."""

    context = zope.interface.Attribute("The context the source is bound to.")
    factory = zope.interface.Attribute("The source factory.")


class INamedSource(zope.interface.Interface):
    """A marker interface to register named source for."""


class IToken(zope.interface.Interface):
    """A string representing a token that uniquely identifies a value."""


# Policies

class ITokenPolicy(zope.interface.Interface):
    """The token policy maps values and tokens."""

    def getValue(source, token):
        """Return a token for the value."""

    def getToken(value):
        """Return a token for the value."""


class IContextualTokenPolicy(zope.interface.Interface):
    """The contextua token policy maps values and tokens.

    It allows access to the context.

    """

    def getValue(context, source, token):
        """Return a token for the value."""

    def getToken(context, value):
        """Return a token for the value."""


class ITermPolicy(zope.interface.Interface):
    """The term policy creates terms and provides data for terms."""

    def createTerm(source, value, title, token, request):
        """Create and return a term object."""

    def getTitle(value):
        """Return a title for the value.

        The return value should not be localized; that is the
        responsibility of the user.  The title may be an
        internationalized message value.

        """


class IContextualTermPolicy(zope.interface.Interface):
    """The contextual term policy creates terms and provides data for terms.

    It allows access to the context.

    """

    def createTerm(context, source, value, title, token, request):
        """Create and return a term object."""

    def getTitle(context, value):
        """Return a title for the value.

        The return value should not be localized; that is the
        responsibility of the user.  The title may be an
        internationalized message value.

        """


class IValuePolicy(zope.interface.Interface):
    """The value policy retrieves and filters values for a source."""

    def getValues():
        """Return the values for the source."""

    def filterValue(value):
        """Determine whether the value should be filtered out or not."""


class IContextualValuePolicy(zope.interface.Interface):
    """The contextual value policy retrieves and filters values for a source
    within context.

    """

    def getValues(context):
        """Return the values for the source in the given context."""

    def filterValue(context, value):
        """Return the values for the source in the given context."""

# Standard combined policies

class ISourcePolicy(ITokenPolicy, ITermPolicy, IValuePolicy):
    pass


class IContextualSourcePolicy(
    ITokenPolicy, IContextualTermPolicy, IContextualValuePolicy):
    pass
