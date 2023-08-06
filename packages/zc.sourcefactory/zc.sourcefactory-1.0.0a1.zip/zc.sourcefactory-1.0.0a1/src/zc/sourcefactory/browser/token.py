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
"""Various token adapters.
"""
import hashlib
import sys

import ZODB.utils
import ZODB.interfaces
import persistent.interfaces

import zope.proxy
import zope.component
import zope.interface

import zc.sourcefactory.interfaces

try:
    unicode
except NameError:
    # Py3: Define unicode
    unicode = str

PY3 = sys.version_info[0] == 3

@zope.component.adapter(bytes)
@zope.interface.implementer(zc.sourcefactory.interfaces.IToken)
def fromString(value):
    # We hash generic strings to be sure they are suitable
    # for URL encoding.
    if not isinstance(value, bytes):
        value = value.encode()
    return hashlib.md5(value).hexdigest()


@zope.component.adapter(unicode)
@zope.interface.implementer(zc.sourcefactory.interfaces.IToken)
def fromUnicode(value):
    value = value.encode("utf-8")
    return fromString(value)


@zope.component.adapter(int)
@zope.interface.implementer(zc.sourcefactory.interfaces.IToken)
def fromInteger(value):
    # We do not have to hash integers as their string representations
    # are definitely suitable for URL encoding.
    return str(value)


@zope.component.adapter(persistent.interfaces.IPersistent)
@zope.interface.implementer(zc.sourcefactory.interfaces.IToken)
def fromPersistent(value):
    # Persistent objects are identified by their oid. If it is persistent but
    # not added to the database, we try to get to the parent, add the value to
    # the database and get the oid then.
    # We have to remove proxies to avoid security here.
    value_unproxied = zope.proxy.removeAllProxies(value)
    try:
        oid = value_unproxied._p_oid
    except AttributeError:
        oid = None

    if oid is None:
        if not hasattr(value, '__parent__'):
            raise ValueError('Can not determine OID for %r' % value)
        connection = ZODB.interfaces.IConnection(value_unproxied.__parent__)
        connection.add(value_unproxied)
        oid = value_unproxied._p_oid
    return ZODB.utils.oid_repr(oid)


@zope.component.adapter(zope.interface.interfaces.IInterface)
@zope.interface.implementer(zc.sourcefactory.interfaces.IToken)
def fromInterface(value):
    # Interface are identified by their module path and name
    return "%s.%s" % (value.__module__, value.__name__)
