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

# import local interfaces

# import Zope3 packages
from z3c.menu.simple.menu import ContextMenuItem

# import local packages

from ztfy.skin import _


class MenuItem(ContextMenuItem):

    @property
    def selected(self):
        return self.request.getURL().endswith('/' + self.viewURL)


class JsMenuItem(MenuItem):

    @property
    def url(self):
        return self.viewURL


class PropertiesMenuItem(MenuItem):

    title = _("Properties")
