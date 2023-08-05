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
from jquery.layer import IJQueryJavaScriptBrowserLayer
from z3c.form.interfaces import IFormLayer
from z3c.jsonrpc.layer import IJSONRPCLayer
from z3c.layer.pagelet import IPageletBrowserLayer

# import local interfaces

# import Zope3 packages

# import local packages


class IBaseZTFYLayer(IFormLayer, IPageletBrowserLayer):
    """Base ZTFY browser layer"""


class IZTFYBrowserLayer(IBaseZTFYLayer, IJQueryJavaScriptBrowserLayer, IJSONRPCLayer):
    """ZTFY JavaScript layer"""


class IZTFYBackLayer(IZTFYBrowserLayer):
    """ZTFY back-office layer"""


class IZTFYFrontLayer(IZTFYBrowserLayer):
    """ZTFY front-office layer"""
