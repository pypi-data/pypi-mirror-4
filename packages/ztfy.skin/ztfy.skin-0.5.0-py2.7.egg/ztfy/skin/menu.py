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
from ztfy.skin.interfaces import IDialogMenu

# import Zope3 packages
from z3c.menu.simple.menu import ContextMenuItem
from zope.interface import implements

# import local packages

from ztfy.skin import _


class MenuItem(ContextMenuItem):

    @property
    def css(self):
        css = getattr(self, 'cssClass', '')
        if self.selected:
            css += ' ' + self.activeCSS
        else:
            css += ' ' + self.inActiveCSS
        if self.title.strip().startswith('::'):
            css += ' submenu'
        return css

    @property
    def selected(self):
        return self.request.getURL().endswith('/' + self.viewURL)


class JsMenuItem(MenuItem):

    @property
    def url(self):
        return self.viewURL


class DialogMenuItem(JsMenuItem):
    """Dialog menu access class"""

    implements(IDialogMenu)

    target = None

    def render(self):
        result = super(DialogMenuItem, self).render()
        if result and (self.target is not None):
            for resource in self.target.resources:
                resource.need()
        return result


class PropertiesMenuItem(MenuItem):

    title = _("Properties")
