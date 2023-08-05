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
from persistent import Persistent

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from ztfy.sequence.interfaces import ISequentialIdInfo, ISequentialIdTarget

# import Zope3 packages
from zope.component import adapter
from zope.interface import implements, implementer
from zope.schema.fieldproperty import FieldProperty

# import local packages


SEQUENCE_INFO_KEY = 'ztfy.sequence'

class SequentialIdInfo(Persistent):
    """Sequential ID info"""

    implements(ISequentialIdInfo)

    oid = FieldProperty(ISequentialIdInfo['oid'])
    hex_oid = FieldProperty(ISequentialIdInfo['hex_oid'])


@adapter(ISequentialIdTarget)
@implementer(ISequentialIdInfo)
def SequentialIdInfoFactory(context):
    annotations = IAnnotations(context)
    info = annotations.get(SEQUENCE_INFO_KEY)
    if info is None:
        info = annotations[SEQUENCE_INFO_KEY] = SequentialIdInfo()
    return info
