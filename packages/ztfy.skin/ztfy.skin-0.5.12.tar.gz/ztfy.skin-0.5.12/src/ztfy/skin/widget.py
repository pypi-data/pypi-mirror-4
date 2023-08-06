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
from z3c.form.interfaces import IWidget, IFieldWidget, IMultiWidget, ITextWidget, IFormLayer, NO_VALUE
from zope.interface.common.idatetime import ITZInfo
from zope.schema.interfaces import IField, IDatetime

# import local interfaces
from ztfy.skin.interfaces import IDateWidget, IDatetimeWidget, IFixedWidthTextAreaWidget
from ztfy.skin.layer import IZTFYBrowserLayer
from ztfy.utils.schema import IDatesRangeField, IColorField, ITextLineListField

# import Zope3 packages
from z3c.form.browser.text import TextWidget
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.browser.widget import HTMLFormElement
from z3c.form.converter import DatetimeDataConverter as BaseDatetimeDataConverter, SequenceDataConverter, FormatterValidationError
from z3c.form.widget import FieldWidget, Widget
from zope.component import adapter, adapts
from zope.i18n.format import DateTimeParseError
from zope.interface import implementer, implements, implementsOnly

# import local packages
from ztfy.jqueryui import jquery_datetime, jquery_colorpicker
from ztfy.skin import ztfy_skin_base


#
# Date and DateTime widgets
#

class DateWidget(TextWidget):
    """Date input widget"""
    implementsOnly(IDateWidget)

    @property
    def pattern(self):
        result = self.request.locale.dates.getFormatter('date', 'short').getPattern()
        return result.replace('d', '%d') \
                     .replace('dd', '%d') \
                     .replace('%d%d', '%d') \
                     .replace('MM', '%m') \
                     .replace('M', '%m') \
                     .replace('yy', '%y')

    def render(self):
        result = super(DateWidget, self).render()
        if result:
            ztfy_skin_base.need()
            jquery_datetime.need()
        return result


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def DateFieldWidget(field, request):
    """IFieldWidget factory for DateField"""
    return FieldWidget(field, DateWidget(request))


class DatetimeWidget(TextWidget):
    """Datetime input widget"""
    implementsOnly(IDatetimeWidget)

    @property
    def pattern(self):
        result = self.request.locale.dates.getFormatter('dateTime', 'short').getPattern()
        return result.replace('d', '%d') \
                     .replace('dd', '%d') \
                     .replace('%d%d', '%d') \
                     .replace('MM', '%m') \
                     .replace('M', '%m') \
                     .replace('yy', '%y') \
                     .replace('HH', '%H') \
                     .replace('h', '%H') \
                     .replace('mm', '%M') \
                     .replace('a', '%p')

    def render(self):
        result = super(DatetimeWidget, self).render()
        if result:
            ztfy_skin_base.need()
            jquery_datetime.need()
        return result


@adapter(IField, IFormLayer)
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
# Dates range widget
#

class IDatesRangeWidget(IMultiWidget):
    """Dates range widget interface"""


class DatesRangeDataConverter(SequenceDataConverter):
    """Dates range data converter"""

    adapts(IDatesRangeField, IDatesRangeWidget)

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return (u'', u'')
        locale = self.widget.request.locale
        formatter = locale.dates.getFormatter('date', 'short')
        return (formatter.format(value[0]) if value[0] else None,
                formatter.format(value[1]) if value[1] else None)

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value
        try:
            locale = self.widget.request.locale
            formatter = locale.dates.getFormatter('date', 'short')
            return (formatter.parse(value[0]) if value[0] else None,
                    formatter.parse(value[1]) if value[1] else None)
        except DateTimeParseError, err:
            raise FormatterValidationError(err.args[0], value)


class DatesRangeWidget(HTMLFormElement, Widget):
    """Dates range widget"""

    implements(IDatesRangeWidget)

    @property
    def pattern(self):
        result = self.request.locale.dates.getFormatter('date', 'short').getPattern()
        return result.replace('dd', '%d').replace('MM', '%m').replace('yy', '%y')

    @property
    def begin_id(self):
        return '%s-begin' % self.id

    @property
    def begin_name(self):
        return '%s.begin' % self.name

    @property
    def begin_date(self):
        return (self.value[0] or '') if self.value else ''

    @property
    def end_id(self):
        return '%s-end' % self.id

    @property
    def end_name(self):
        return '%s.end' % self.name

    @property
    def end_date(self):
        return (self.value[1] or '') if self.value else ''

    def extract(self, default=NO_VALUE):
        begin_date = self.request.get(self.begin_name)
        end_date = self.request.get(self.end_name)
        return (begin_date, end_date)

    def render(self):
        result = super(DatesRangeWidget, self).render()
        if result:
            ztfy_skin_base.need()
            jquery_datetime.need()
        return result


@adapter(IDatesRangeField, IFormLayer)
@implementer(IFieldWidget)
def DatesRangeFieldWidgetFactory(field, request):
    """IDatesRangeField widget factory"""
    return FieldWidget(field, DatesRangeWidget(request))


#
# Color widget
#

class IColorWidget(ITextWidget):
    """Color widget interface"""


class ColorWidget(TextWidget):
    """Color widget"""

    implementsOnly(IColorWidget)

    def render(self):
        result = super(ColorWidget, self).render()
        if result:
            ztfy_skin_base.need()
            jquery_colorpicker.need()
        return result


@adapter(IColorField, IFormLayer)
@implementer(IFieldWidget)
def ColorFieldWidgetFactory(field, request):
    """IColorField widget factory"""
    return FieldWidget(field, ColorWidget(request))


#
# Textline list widget
#

class ITextLineListWidget(ITextWidget):
    """TextLineList widget interface"""


class TextLineListDataConverter(SequenceDataConverter):
    """TextLineList field data converter"""

    adapts(ITextLineListField, IWidget)

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return []
        return '|'.join(value)

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value
        return value.split('|')


class TextLineListWidget(TextWidget):
    """TextLineList field widget"""

    implementsOnly(ITextLineListWidget)

    def render(self):
        result = super(TextLineListWidget, self).render()
        if result:
            ztfy_skin_base.need()
        return result


@adapter(ITextLineListField, IFormLayer)
@implementer(IFieldWidget)
def TextLineListFieldWidgetFactory(field, request):
    return FieldWidget(field, TextLineListWidget(request))


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
