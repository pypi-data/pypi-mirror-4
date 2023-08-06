### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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
from z3c.formui.interfaces import IFormUILayer
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserSkinType
from zope.traversing.interfaces import IBeforeTraverseEvent

# import local interfaces
from ztfy.skin.interfaces import ISkinnable
from ztfy.skin.layer import IBaseZTFYLayer, IZTFYBrowserLayer, \
                            IZTFYBackLayer, IZTFYFrontLayer

# import Zope3 packages
from zope.component import adapter, queryUtility
from zope.publisher.skinnable import applySkin

# import local packages


class IBaseZTFYSkin(IFormUILayer, IBaseZTFYLayer):
    """The ZTFY browser skin, using a skin-based form layout"""


class IZTFYSkin(IBaseZTFYSkin, IZTFYBrowserLayer):
    """The ZTFY base JavaScript skin"""


class IZTFYBackSkin(IZTFYSkin, IZTFYBackLayer):
    """ZTFY back-office skin"""


class IZTFYFrontSkin(IZTFYSkin, IZTFYFrontLayer):
    """ZTFY front-office skin"""


@adapter(ISkinnable, IBeforeTraverseEvent)
def handleSkinTraversal(object, event):
    if IBrowserRequest.providedBy(event.request):
        path = event.request.get('PATH_INFO', '')
        if (path.find('++skin++') < 0):
            skin_name = ISkinnable(object).getSkin()
            if not skin_name:
                skin_name = 'ZBlog'
            skin = queryUtility(IBrowserSkinType, skin_name)
            if skin is not None:
                applySkin(event.request, skin)
