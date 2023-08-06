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
from z3c.json.interfaces import IJSONWriter
from zope.authentication.interfaces import IAuthentication, ILogout
from zope.component.interfaces import ISite

# import local interfaces

# import Zope3 packages
from z3c.formjs import ajax
from zope.component import  adapts, getUtility, getUtilitiesFor, hooks
from zope.interface import implements

# import local packages
from ztfy.utils.traversing import getParent


class LogoutAdapter(object):

    adapts(IAuthentication)
    implements(ILogout)

    def __init__(self, auth):
        self.auth = auth

    def logout(self, request):
        return self.auth.logout(request)


class LoginLogoutView(ajax.AJAXRequestHandler):
    """Base login/logout view"""

    @ajax.handler
    def login(self):
        writer = getUtility(IJSONWriter)
        context = getParent(self.context, ISite)
        while context is not None:
            old_site = hooks.getSite()
            try:
                hooks.setSite(context)
                for _name, auth in getUtilitiesFor(IAuthentication):
                    if auth.authenticate(self.request) is not None:
                        return writer.write('OK')
            finally:
                hooks.setSite(old_site)
            context = getParent(context, ISite, allow_context=False)
        return writer.write('NOK')

    @ajax.handler
    def logout(self):
        writer = getUtility(IJSONWriter)
        context = getParent(self.context, ISite)
        while context is not None:
            old_site = hooks.getSite()
            try:
                hooks.setSite(context)
                for _name, auth in getUtilitiesFor(IAuthentication):
                    if auth.logout(self.request):
                        return writer.write('OK')
            finally:
                hooks.setSite(old_site)
            context = getParent(context, ISite, allow_context=False)
        return writer.write('NOK')
