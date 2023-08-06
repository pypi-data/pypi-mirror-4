### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
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
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces

# import Zope3 packages
from zope.traversing.api import getName

# import local packages
from ztfy.skin.viewlet import ViewletBase


class TitleViewlet(ViewletBase):
    """Title viewlet"""

    @property
    def title(self):
        try:
            title = self.__parent__.title
        except AttributeError:
            title = getattr(self.context, 'title', None)
            if title is None:
                dc = IZopeDublinCore(self.context, None)
                if dc is not None:
                    title = dc.title
        if not title:
            title = '[ %s ]' % getName(self.context)
        return title
