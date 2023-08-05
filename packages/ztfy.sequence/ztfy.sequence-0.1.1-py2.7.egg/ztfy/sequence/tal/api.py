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
from zope.tales.interfaces import ITALESFunctionNamespace
from ztfy.sequence.tal.interfaces import ISequentialIdTalesAPI

# import local interfaces

# import Zope3 packages
from zope.interface import implements
from ztfy.sequence.interfaces import ISequentialIdInfo

# import local packages


class SequentialIdTalesAPI(object):
    """Sequential ID TALES API"""

    implements(ISequentialIdTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def oid(self):
        return ISequentialIdInfo(self.context).oid
