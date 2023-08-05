### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages

# import Zope3 interfaces
from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectCopiedEvent, IObjectRemovedEvent

# import local interfaces
from ztfy.sequence.interfaces import ISequentialIntIds, ISequentialIdTarget, ISequentialIdInfo

# import Zope3 packages
from zope.component import adapter, queryUtility
from zope.interface import implements
from zope.intid import IntIds
from zope.schema.fieldproperty import FieldProperty

# import local packages


class SequentialIntIds(IntIds):
    """Sequential IDs utility"""

    implements(ISequentialIntIds)

    prefix = FieldProperty(ISequentialIntIds['prefix'])
    hex_oid_length = FieldProperty(ISequentialIntIds['hex_oid_length'])

    _lastId = 0

    def _generateId(self):
        self._lastId += 1
        return self._lastId

    def register(self, ob):
        if not ISequentialIdTarget.providedBy(ob):
            return None
        return super(SequentialIntIds, self).register(ob)

    def generateHexId(self, obj, oid):
        return (u'%%s%%s%%.%dx' % self.hex_oid_length) % (self.prefix or '',
                                                          getattr(obj, 'prefix', ''),
                                                          oid)


@adapter(ISequentialIdTarget, IObjectAddedEvent)
def handleNewSequentialIdTarget(obj, event):
    """Set unique ID for each added object"""
    utility = queryUtility(ISequentialIntIds, getattr(obj, 'sequence_name', ''))
    if utility is not None:
        info = ISequentialIdInfo(obj)
        if not info.oid:
            oid = info.oid = utility.register(obj)
            info.hex_oid = utility.generateHexId(obj, oid)


@adapter(ISequentialIdTarget, IObjectCopiedEvent)
def handleCopiedSequentialIdTarget(obj, event):
    """Reset unique ID when an object is copied"""
    info = ISequentialIdInfo(obj)
    info.oid = None
    info.hex_oid = None


@adapter(ISequentialIdTarget, IObjectRemovedEvent)
def handleRemovedSequentialIdTarget(obj, event):
    """Unregister object when it is removed"""
    utility = queryUtility(ISequentialIntIds, getattr(obj, 'sequence_name', ''))
    if (utility is not None) and (utility.queryId(obj) is not None):
        utility.unregister(obj)
