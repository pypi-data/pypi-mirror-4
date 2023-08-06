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
from z3c.language.switch.interfaces import II18n
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.skin.interfaces import IDefaultView, IBreadcrumbInfo

# import Zope3 packages
from zope.component import queryMultiAdapter
from zope.traversing.api import getParents
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.skin.viewlet import ViewletBase


class BreadcrumbsViewlet(ViewletBase):

    viewname = ''

    @property
    def crumbs(self):
        result = []
        for parent in reversed([self.context, ] + getParents(self.context)):
            info = queryMultiAdapter((parent, self.request, self.__parent__), IBreadcrumbInfo)
            if info is not None:
                result.append({ 'title': info.title,
                                'path': info.path,
                                'class': '' })
            else:
                i18n = II18n(parent, None)
                if i18n is not None:
                    name = i18n.queryAttribute('shortname', request=self.request) or i18n.queryAttribute('title', request=self.request)
                else:
                    dc = IZopeDublinCore(parent, None)
                    if dc is not None:
                        name = dc.title
                if name:
                    adapter = queryMultiAdapter((parent, self.request, self.__parent__), IDefaultView)
                    if (adapter is not None) and adapter.viewname:
                        self.viewname = '/' + adapter.viewname
                    result.append({ 'title': name,
                                    'path': '%s%s' % (absoluteURL(parent, request=self.request),
                                                      self.viewname),
                                    'class': '' })
        if result:
            result[-1]['class'] = 'current'
        return result
