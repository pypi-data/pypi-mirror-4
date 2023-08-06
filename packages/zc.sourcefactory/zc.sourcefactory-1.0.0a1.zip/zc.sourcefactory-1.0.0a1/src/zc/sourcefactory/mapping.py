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
"""A source proxy providing a mapping between values

"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema.interfaces


@zope.interface.implementer(zope.schema.interfaces.IContextSourceBinder)
class ValueMappingSourceContextBinder(object):

    def __init__(self, base, map):
        self.base = base
        self.map = map

    def __call__(self, context):
        source = self.base(context)
        return ValueMappingSource(source, self.map)


@zope.interface.implementer(zope.schema.interfaces.IIterableSource)
class ValueMappingSource(object):

    def __init__(self, base, map):
        self.base = base
        self._mapping_cache = {}
        self.map = map

    def mapReverse(self, mapped_value):
        if mapped_value in self._mapping_cache:
            return self._mapping_cache[mapped_value]

        # Not found in cache, continue to look for the mapped value in
        # the rest of the iterator
        if not hasattr(self, '_cache_iterator'):
            self._cache_iterator = iter(self.base)
        for original_value in self._cache_iterator:
            original_mapped_value = self.map(original_value)
            self._mapping_cache[original_mapped_value] = original_value
            if mapped_value == original_mapped_value:
                return original_value
        raise KeyError(mapped_value)

    def __contains__(self, value):
        try:
            self.mapReverse(value)
        except KeyError:
            return False
        else:
            return True

    def __iter__(self):
        for item in self.base:
            yield self.map(item)

    def __len__(self):
        return len(self.base)

    def __bool__(self):
        for dummy in self.base:
            return True
        return False

    __nonzero__ = __bool__
