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
from z3c.form.interfaces import IFieldWidget
from zope.interface.common.idatetime import ITZInfo
from zope.schema.interfaces import IField, IDatetime

# import local interfaces
from ztfy.skin.interfaces import IDateWidget, IDatetimeWidget, IFixedWidthTextAreaWidget
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.form.browser.text import TextWidget
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.converter import DatetimeDataConverter as BaseDatetimeDataConverter
from z3c.form.widget import FieldWidget
from zope.component import adapter, adapts
from zope.interface import implementer, implementsOnly

# import local packages
from ztfy.jqueryui import jquery_datetime


#
# Date and DateTime widgets
#

class DateWidget(TextWidget):
    """Date input widget"""
    implementsOnly(IDateWidget)

    @property
    def needed(self):
        jquery_datetime.need()

    @property
    def pattern(self):
        result = self.request.locale.dates.getFormatter('date', 'short').getPattern()
        return result.replace('dd', '%d').replace('MM', '%m').replace('yy', '%y')


@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def DateFieldWidget(field, request):
    """IFieldWidget factory for DateField"""
    return FieldWidget(field, DateWidget(request))


class DatetimeWidget(TextWidget):
    """Datetime input widget"""
    implementsOnly(IDatetimeWidget)

    @property
    def needed(self):
        jquery_datetime.need()

    @property
    def pattern(self):
        result = self.request.locale.dates.getFormatter('dateTime', 'short').getPattern()
        return result.replace('dd', '%d').replace('MM', '%m').replace('yy', '%y').replace('HH', '%H').replace('mm', '%M')


@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def DatetimeFieldWidget(field, request):
    """IFieldWidget factory for DatetimeField"""
    return FieldWidget(field, DatetimeWidget(request))


class DatetimeDataConverter(BaseDatetimeDataConverter):

    adapts(IDatetime, IDatetimeWidget)

    def toFieldValue(self, value):
        value = super(DatetimeDataConverter, self).toFieldValue(value)
        if value and not value.tzinfo:
            tz = ITZInfo(self.widget.request)
            value = tz.localize(value)
        return value


#
# Fixed width text area widget
#

class FixedWidthTextAreaWidget(TextAreaWidget):
    """Custom fixed width text area widget"""
    implementsOnly(IFixedWidthTextAreaWidget)


@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def FixedWidthTextAreaFieldWidget(field, request):
    """IFixedWidthTextAreaWidget factory"""
    return FieldWidget(field, FixedWidthTextAreaWidget(request))
