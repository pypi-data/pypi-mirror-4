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
from zope.annotation.interfaces import IAttributeAnnotatable

# import local interfaces

# import Zope3 packages
from zope.interface import Interface
from zope.schema import TextLine, Int

# import local packages

from ztfy.sequence import _


class ISequentialIntIds(Interface):
    """Sequential IntIds utility interface"""

    prefix = TextLine(title=_("Hexadecimal prefix"),
                      description=_("Prefix used to generate hexadecimal ID"),
                      required=False,
                      max_length=10)

    hex_oid_length = Int(title=_("Hexadecimal ID length"),
                         description=_("Full length of hexadecimal ID, not including prefix"),
                         min=0,
                         max=20,
                         default=10)

    def generateHexId(self, obj, oid):
        """Generate an hexadecimal ID for the given sequence"""


class ISequentialIdInfo(Interface):
    """Sequential ID info interface"""

    oid = Int(title=_("Sequential ID"),
              required=False)

    hex_oid = TextLine(title=_("Sequential ID in hexadecimal form"),
                       required=False)


class ISequentialIdTarget(IAttributeAnnotatable):
    """Marker interface used to identify classes which have to get a unique sequential ID"""

    sequence_name = TextLine(title=_("Sequence name"),
                             description=_("Name of sequence utility used to get unique IDs"),
                             required=False)

    prefix = TextLine(title=_("Hexadecimal prefix"),
                      description=_("""Prefix used to generate hexadecimal ID, placed after utility prefix.
                                       Generally defined at class level."""),
                      required=False)
