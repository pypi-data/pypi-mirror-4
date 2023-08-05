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

# import local interfaces
from ztfy.sequence.interfaces import ISequentialIntIds
from ztfy.skin.interfaces import IDefaultView, IPropertiesMenuTarget
from ztfy.skin.layer import IZTFYBackLayer

# import Zope3 packages
from z3c.form import field
from zope.component import adapts
from zope.interface import implements, Interface
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.skin.form import EditForm


class SequentialIntIdsUtilityDefaultViewAdapter(object):
    """Sequential ID utility default view adapter"""

    adapts(ISequentialIntIds, IZTFYBackLayer, Interface)
    implements(IDefaultView)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    @property
    def viewname(self):
        return '@@properties.html'

    def getAbsoluteURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request), self.viewname)


class SequentialIntIdsUtilityEditForm(EditForm):
    """Sequential ID utility edit form"""

    implements(IPropertiesMenuTarget)

    fields = field.Fields(ISequentialIntIds)
