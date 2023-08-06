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

# import local interfaces
from ztfy.skin.interfaces import ICustomBackOfficeInfoTarget

# import Zope3 packages
from zope.component import queryAdapter
from zope.traversing import namespace

# import local packages
from ztfy.utils.traversing import getParent


class CustomBackOfficeInfoNamespace(namespace.view):
    """++back++ namespace traverser"""

    def traverse(self, name, ignored):
        target = getParent(self.context, ICustomBackOfficeInfoTarget)
        if target is not None:
            return queryAdapter(target, target.back_interface)
