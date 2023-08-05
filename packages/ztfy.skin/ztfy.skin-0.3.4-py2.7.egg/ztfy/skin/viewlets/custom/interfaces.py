### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#
##############################################################################


# import standard packages

# import Zope3 interfaces
from zope.viewlet.interfaces import IViewletManager

# import local interfaces

# import Zope3 packages
from zope.interface import Attribute
from zope.schema import Int

# import local packages

from ztfy.skin import _


class ICustomViewletManagerHandler(IViewletManager):
    """Custom viewlets managers handler, based on adapters"""

    managers = Attribute(_("Custom viewlet managers list"))


class ICustomViewletManager(IViewletManager):
    """Custom viewlet manager interface"""

    weight = Int(title=_("Viewlet manager weight"),
                 default=0)
