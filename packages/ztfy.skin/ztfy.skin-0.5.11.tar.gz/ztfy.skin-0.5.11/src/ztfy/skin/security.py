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
from z3c.form.interfaces import HIDDEN_MODE
from z3c.json.interfaces import IJSONWriter
from zope.authentication.interfaces import IAuthentication, ILogout
from zope.component.interfaces import ISite
from zope.security.interfaces import IUnauthorized

# import local interfaces
from ztfy.skin.interfaces import IDefaultView, ILoginFormFields

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import ajax
from zope.component import  adapts, queryMultiAdapter, getUtility, getUtilitiesFor, hooks
from zope.interface import implements
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.skin.form import AddForm
from ztfy.utils.traversing import getParent

from ztfy.skin import _


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


class LoginForm(AddForm):
    """ZMI login form"""

    title = _("Login form")
    legend = _("Please enter valid credentials to login")

    fields = field.Fields(ILoginFormFields)

    def __call__(self):
        self.request.response.setStatus(401)
        return super(LoginForm, self).__call__()

    def updateWidgets(self):
        super(LoginForm, self).updateWidgets()
        self.widgets['came_from'].mode = HIDDEN_MODE
        if IUnauthorized.providedBy(self.context):
            self.widgets['came_from'].value = self.request.getURL()

    @button.buttonAndHandler(_("login-button", "Login"))
    def handleLogin(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.request.form['login'] = data['username']
        self.request.form['password'] = data['password']
        if IUnauthorized.providedBy(self.context):
            context, _layer, _permission = self.context.args
        else:
            context = self.context
        site = getParent(context, ISite)
        while site is not None:
            old_site = hooks.getSite()
            try:
                hooks.setSite(site)
                for _name, auth in getUtilitiesFor(IAuthentication):
                    if auth.authenticate(self.request) is not None:
                        target = data.get('came_from')
                        if target:
                            self.request.response.redirect(target)
                        else:
                            target = queryMultiAdapter((context, self.request, self), IDefaultView)
                            if target is not None:
                                self.request.response.redirect(target.getAbsoluteURL())
                            else:
                                self.request.response.redirect('%s/@@SelectedManagementView.html' % absoluteURL(self.context, self.request))
                        return u''
            finally:
                hooks.setSite(old_site)
            site = getParent(site, ISite, allow_context=False)
