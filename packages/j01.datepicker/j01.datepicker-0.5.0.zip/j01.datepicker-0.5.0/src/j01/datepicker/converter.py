##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.i18n.format
import zope.component
import zope.schema.interfaces

import z3c.form.converter

from j01.datepicker import interfaces


class DatePickerConverter(z3c.form.converter.BaseDataConverter):
    """A special data converter for IDatePickerWidget."""
    zope.component.adapts(
        zope.schema.interfaces.IDate, interfaces.IDatePickerWidget)

    type = 'date'

    def __init__(self, field, widget):
        super(DatePickerConverter, self).__init__(field, widget)
        locale = self.widget.request.locale
        self.formatter = locale.dates.getFormatter(self.type,
            self.widget.formatterLength)

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return u''
        # format based on the widgets settings
        return self.formatter.format(value, self.widget.dateFormatPattern)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        try:
            # parse based on the widgets settings
            return self.formatter.parse(value,
                pattern=self.widget.dateFormatPattern)
        except zope.i18n.format.DateTimeParseError, err:
            raise z3c.form.converter.FormatterValidationError(err.args[0],
                value)


class DatePickerForDatetimeConverter(z3c.form.converter.BaseDataConverter):
    """DatePicker date for datetime converter."""
    zope.component.adapts(
        zope.schema.interfaces.IDatetime, interfaces.IDatePickerWidget)

    type = 'dateTime'

    def __init__(self, field, widget):
        super(DatePickerForDatetimeConverter, self).__init__(field, widget)
        locale = self.widget.request.locale
        self.formatter = locale.dates.getFormatter(self.type,
            self.widget.formatterLength)

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return u''
        # format based on the widgets settings
        return self.formatter.format(value, self.widget.dateFormatPattern)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        try:
            # first append time string and enhance date pattern with time
            value = '%s %s' % (value, self.widget.timeAppendix)
            pattern = '%s H:M:S' % self.widget.dateFormatPattern
            # parse based on the widgets settings
            dt = self.formatter.parse(value, pattern=pattern)
            return dt.replace(tzinfo=self.widget.tzinfo)
        except zope.i18n.format.DateTimeParseError, err:
            try:
                self.formatter.format(value, self.widget.dateFormatPattern)
            except zope.i18n.format.DateTimeParseError, err:
                raise z3c.form.converter.FormatterValidationError(err.args[0],
                    value)
