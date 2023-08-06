### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from zope.intid.interfaces import IIntIds
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.skin.viewlets.properties.interfaces import IPropertiesViewletManager

# import Zope3 packages
from zope.component import getUtility
from zope.interface import implements
from zope.viewlet.manager import WeightOrderedViewletManager

# import local packages
from ztfy.skin.viewlet import ViewletBase
from ztfy.utils.security import getPrincipal
from ztfy.utils.timezone import tztime


class PropertiesViewletManager(WeightOrderedViewletManager):

    implements(IPropertiesViewletManager)


class PropertiesViewlet(ViewletBase):
    """Default properties viewlet"""

    def principal(self, uid):
        return getPrincipal(uid)

    @property
    def oid(self):
        intids = getUtility(IIntIds)
        return intids.register(self.context)

    @property
    def creator(self):
        dc = IZopeDublinCore(self.context, None)
        if dc is not None:
            uid = dc.creators[0]
            return getPrincipal(uid)

    @property
    def created(self):
        dc = IZopeDublinCore(self.context, None)
        if dc is not None:
            return tztime(dc.created)

    @property
    def modified(self):
        dc = IZopeDublinCore(self.context, None)
        if dc is not None:
            return tztime(dc.modified)
