### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#
##############################################################################


# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.skin.viewlets.custom.interfaces import ICustomViewletManagerHandler, \
                                                 ICustomViewletManager

# import Zope3 packages
from zope.component import getAdapters
from zope.interface import implements
from zope.viewlet.manager import WeightOrderedViewletManager

# import local packages
from ztfy.utils.property import cached_property


class CustomViewletManagerHandler(WeightOrderedViewletManager):
    """Custom viewlet manager based on adapters"""

    implements(ICustomViewletManagerHandler)

    @cached_property
    def managers(self):
        adapters = getAdapters((self.context, self.request, self.__parent__), ICustomViewletManager)
        return sorted((adapter for _name, adapter in adapters),
                      key=lambda x: x.weight)

    def update(self):
        [ manager.update() for manager in self.managers ]

    def render(self):
        return '\n'.join((manager.render() for manager in self.managers))
