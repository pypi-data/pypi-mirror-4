### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
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
from z3c.template.interfaces import IPageTemplate
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.skin.interfaces import IContainerBaseView, IOrderedContainerBaseView, \
                                 IContainerAddFormMenuTarget, \
                                 IOrderedContainerSorterColumn, IOrderedContainer

# import Zope3 packages
from z3c.formjs import ajax
from z3c.table.column import Column
from z3c.table.table import Table
from z3c.template.template import getViewTemplate, getPageTemplate
from zope.i18n import translate
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.traversing.api import getName

# import local packages
from ztfy.jqueryui import jquery_ui_css, jquery_jsonrpc, jquery_ui_base
from ztfy.skin.menu import MenuItem
from ztfy.skin.page import BaseBackView, TemplateBasedPage

from ztfy.skin import _


class ContainerContentsViewMenu(MenuItem):
    """Container contents menu"""

    title = _("Contents")


class OrderedContainerSorterColumn(Column):

    implements(IOrderedContainerSorterColumn)

    header = u''
    weight = 1
    cssClasses = { 'th': 'sorter' }

    def renderCell(self, item):
        return '<img class="handler" src="/--static--/ztfy.skin/img/sort.png" />'


class ContainerBaseView(BaseBackView, TemplateBasedPage, Table):
    """Container-like base view"""

    implements(IContainerBaseView)

    legend = _("Container's content")
    empty_message = _("This container is empty")

    batchSize = 25
    startBatchingAt = 25

    output = getViewTemplate()

    def __init__(self, context, request):
        super(ContainerBaseView, self).__init__(context, request)
        Table.__init__(self, context, request)

    @property
    def title(self):
        result = None
        i18n = II18n(self.context, None)
        if i18n is not None:
            result = II18n(self.context).queryAttribute('title', request=self.request)
        if result is None:
            dc = IZopeDublinCore(self.context, None)
            if dc is not None:
                result = dc.title
        if not result:
            result = '{{ %s }}' % getName(self.context)
        return result

    @property
    def empty_value(self):
        return translate(self.empty_message, context=self.request)

    def update(self):
        super(ContainerBaseView, self).update()
        Table.update(self)
        jquery_ui_css.need()
        jquery_jsonrpc.need()


class OrderedContainerBaseView(ajax.AJAXRequestHandler, ContainerBaseView):

    implements(IOrderedContainerBaseView, IContainerAddFormMenuTarget)

    sortOn = None
    interface = None
    container_interface = IOrderedContainer

    batchSize = 10000
    startBatchingAt = 10000

    cssClasses = { 'table': 'orderable' }

    def update(self):
        super(OrderedContainerBaseView, self).update()
        jquery_ui_base.need()
        jquery_jsonrpc.need()

    @ajax.handler
    def ajaxUpdateOrder(self, *args, **kw):
        self.updateOrder()

    def updateOrder(self, context=None):
        ids = self.request.form.get('ids', [])
        if ids:
            if context is None:
                context = self.context
            container = self.container_interface(context)
            container.updateOrder(ids, self.interface)


class InnerContainerBaseView(Table):
    """A container table displayed inside another view"""

    template = getPageTemplate()

    def __init__(self, view, request):
        Table.__init__(self, view.context, request)
        self.__parent__ = view
        self.__name__ = u''

    def render(self):
        if self.template is None:
            template = getMultiAdapter((self, self.request), IPageTemplate)
            return template(self)
        return self.template()
