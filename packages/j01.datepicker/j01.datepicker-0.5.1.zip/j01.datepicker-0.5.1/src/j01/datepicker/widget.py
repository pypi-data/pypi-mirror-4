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

import datetime

import zope.interface
import zope.component
import zope.i18n
import zope.i18nmessageid

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.text

from j01.datepicker import UTC
from j01.datepicker import interfaces


_ = zope.i18nmessageid.MessageFactory('p01')


# i18n
DAYS = [
    _('Sunday'),
    _('Monday'),
    _('Tuesday'),
    _('Wednesday'),
    _('Thursday'),
    _('Friday'),
    _('Saturday'),
    _('Sunday'), # yes, that's correct
    ]


DAYS_SHORT = [
    _('Sun'),
    _('Mon'),
    _('Tue'),
    _('Wed'),
    _('Thu'),
    _('Fri'),
    _('Sat'),
    _('Sun'), # yes, that's correct
    ]

DAYS_MIN = [
    _('Su'),
    _('Mo'),
    _('Tu'),
    _('We'),
    _('Th'),
    _('Fr'),
    _('Sa'),
    _('Su'),
    ]

MONTHS = [
    _('January'),
    _('February'),
    _('March'),
    _('April'),
    _('May'),
    _('June'),
    _('July'),
    _('August'),
    _('September'),
    _('October'),
    _('November'),
    _('December'),
    ]

MONTHS_SHORT = [
    _('Jan'),
    _('Feb'),
    _('Mar'),
    _('Apr'),
    _('May'),
    _('Jun'),
    _('Jul'),
    _('Aug'),
    _('Sep'),
    _('Oct'),
    _('Nov'),
    _('Dec'),
    ]


# l10n
# provide date format pattern translation
defaultDateFormatPattern = u'MM.dd.yyyy'
defaultDatePickerFormatPattern = u'm.d.Y'

# suported date formats
# we will ensure that we only support and use the follwing date formats
# any other format is not supported
dateLocales = {
    'dd.MM.yyyy': _(u'dd.MM.yyyy'),
    'dd/MM/yyyy': _(u'dd/MM/yyyy'),
    'dd-MM-yyyy': _(u'dd-MM-yyyy'),
    'MM.dd.yyyy': _(u'MM.dd.yyyy'),
    'MM/dd/yyyy': _(u'MM/dd/yyyy'),
    'MM-dd-yyyy': _(u'MM-dd-yyyy'),
}


def getDateFormatPattern(pattern):
    if pattern in dateLocales:
        return pattern
    elif pattern is not None and pattern.lower().startswith('d'):
        return 'dd.MM.yyyy'
    else:
        return defaultDateFormatPattern


def getDatePickerFormatPattern(pattern):
    """Return the datepicker format based on the given pattern"""
    if pattern in dateLocales:
        patter = pattern.replace('dd', 'd')
        patter = pattern.replace('MM', 'm')
        patter = pattern.replace('yyyy', 'Y')
    elif pattern is not None and pattern.lower().startswith('d'):
        pattern = u'd.m.Y'
    else:
        pattern = defaultDatePickerFormatPattern
    return pattern


J01_DATEPICKER_TEMPLATE = """
<script type="text/javascript">
  $(document).ready(function(){
    $("%(expression)s").DatePicker({%(settings)s});
  });
</script>
"""

ON_BEFORE_SHOW_TEMPLATE = """function(){
        var val = $('%s').val();
        if (val) {
            $('%s').DatePickerSetDate(val, false);
        }
    }"""

ON_CHANGE_TEMPLATE = """function(formated, dates){
        $('%s').val(formated);
        $('%s').DatePickerHide();
    }"""

ON_RENDER_SKIP_PAST_DATE_TEMPLATE = """function(date) {
        var now = new Date();
        now.setHours(0,0,0,0);
        var disabled = (date.valueOf() < now.valueOf())? true: false;
        var clsName = (date.valueOf() == now.valueOf())? 'datepickerCurrent': false;
    	return {disabled: disabled, className: clsName}
    }"""

ON_RENDER_TEMPLATE = """function(date) {
        var now = new Date();
        var clsName = date.valueOf() == now.valueOf() ? 'datepickerCurrent' : false
    	return {className: clsName}
    }"""


# javascript
def j01DatePickerJavaScript(j01DatePickerExpression, data):
    """DatePicker JavaScript generator
    
    simple date picker widget script
    $('#date').DatePicker({
        flat: true,
        date: '2008-07-31',
        current: '2008-07-31',
        calendars: 1,
        starts: 1,
        view: 'years'
    });

    flat: false,
    starts: 1,
    prev: '&#9664;',
    next: '&#9654;',
    lastSel: false,
    mode: 'single',
    view: 'days',
    calendars: 1,
    format: 'Y-m-d',
    position: 'bottom',
    eventName: 'click',
    onRender: function(){return {};},
    onChange: function(){return true;},
    onShow: function(){return true;},
    onBeforeShow: function(){return true;},
    onHide: function(){return true;},
    locale: {
        days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        daysShort: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        daysMin: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
        months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        monthsShort: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        weekMin: "wk"
    }

    """
    lines = []
    append = lines.append
    for key, value in data.items():
        if key == 'locale':
            l = ['\n        %s: %s' % (k, v) for k, v in value.items()]
            append("\n    locale: {%s}" % ','.join(l))
        elif key in ['onRender', 'onChange', 'onShow', 'onBeforeShow', 'onHide']:
            append("\n    %s: %s" % (key, value))
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif value is None:
            append("\n    %s: null" % key)
        elif isinstance(value, int):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, (str, unicode)):
            if value.startswith('$'):
                append("\n    %s: %s" % (key, value))
            else:
                append("\n    %s: '%s'" % (key, value))
        else:
            append("\n    %s: %s" % (key, value))
    settings = ','.join(lines)
    return J01_DATEPICKER_TEMPLATE % ({'expression': j01DatePickerExpression,
                                       'settings': settings})


# date widget
class DatePickerWidget(z3c.form.browser.text.TextWidget):
    """Upload widget implementation."""

    zope.interface.implementsOnly(interfaces.IDatePickerWidget)

    klass = u'j01DatePickerWidget'
    css = u'j01-datepicker'

    formatterLength = 'short'

    # timeAppendix is only used in datetime convert for correct the appended
    # time. see: DatePickerForDatetimeConverter for more info
    # We can use startDate = '00:00:00' and endDate = '23:59:59'
    # this will make sure we have almost a full day stored between startDate 
    # and endDate but at the same time we can show the same date value
    timeAppendix = '00:00:00'

    territory = None

    # config
    flat = False
    starts = 1
    # support twitter bootstrap icons with fallback to arrow
    prev = '&lsaquo;' # '&#9664;'
    next = '&rsaquo;' # '&#9654;'
    lastSel = False
    _mode = 'single' # mode is used in widget, use _mode
    view = 'days'
    calendars = 1
    position = 'bottom'
    eventName = 'click'

    skipPastDates = False

    _label = None
    appendLabelDatePattern = True

    def translate(self, msg):
        return zope.i18n.translate(msg, context=self.request)

    def getLabel(self):
        if self.appendLabelDatePattern:
            # translate and append date pattern to label
            label = self.translate(self._label)
            pattern = self.translate(self.dateFormatPattern)
            return '%s (%s)' % (label, pattern)
        else:
            # return plain label
            return self._label

    @apply
    def label():
        def fget(self):
            return self.getLabel()
        def fset(self, value):
            # set plain field title as value
            self._label = value
        return property(fget, fset)

    @property
    def tzinfo(self):
        return UTC

    @property
    def dateFormatPattern(self):
        return getDateFormatPattern(self.pattern)

    @property
    def datePickerFormatPattern(self):
        return getDatePickerFormatPattern(self.pattern)

    @property
    def days(self):
        return [self.translate(d).encode('utf-8') for d in DAYS]

    @property
    def daysShort(self):
        return [self.translate(d).encode('utf-8') for d in DAYS_SHORT]

    @property
    def daysMin(self):
        return [self.translate(d).encode('utf-8') for d in DAYS_MIN]

    @property
    def months(self):
        return [self.translate(d).encode('ascii', 'xmlcharrefreplace')
                for d in MONTHS]

    @property
    def monthsShort(self):
        return [self.translate(d).encode('ascii', 'xmlcharrefreplace')
                for d in MONTHS_SHORT]

    @property
    def weekMin(self):
        return self.translate(_(u'wk'))

    @property
    def locale(self):
        return {'days': self.days,
                'daysShort': self.daysShort,
                'daysMin': self.daysMin,
                'months': self.months,
                'monthsShort': self.monthsShort,
                'weekMin': "'%s'" % self.weekMin
            }

    @property
    def onRender(self):
        # by default we mark the current day with datepickerCurrent style
        if self.skipPastDates:
            # this disables previous date selection
            return ON_RENDER_SKIP_PAST_DATE_TEMPLATE
        else:
            return ON_RENDER_TEMPLATE

    @property
    def onChange(self):
        expr = self.j01DatePickerExpression
        return ON_CHANGE_TEMPLATE % (expr, expr)

    @property
    def onShow(self):
        return 'function(){return true;}'

    @property
    def onBeforeShow(self):
        expr = self.j01DatePickerExpression
        return ON_BEFORE_SHOW_TEMPLATE % (expr, expr)

    @property
    def onHide(self):
        return 'function(){return true;}'

    @property
    def date(self):
        return "$('%s').val()" % self.j01DatePickerExpression

    @property
    def current(self):
        today = datetime.date.today()
        locale = self.request.locale
        formatter = locale.dates.getFormatter('date', self.formatterLength)
        return formatter.format(today, self.dateFormatPattern)

    @property
    def j01DatePickerExpression(self):
        return '#%s' % self.id.replace('.', '\\\.')

    @property
    def j01DatePickerJavaScript(self):
        data = {
            'date': self.date,
            'current': self.current,
            'flat': self.flat,
            'starts': self.starts,
            'prev': self.prev,
            'next': self.next,
            'lastSel': self.lastSel,
            'mode': self._mode,
            'view': self.view,
            'calendars': self.calendars,
            'format': self.datePickerFormatPattern,
            'position': self.position,
            'eventName': self.eventName,
            'locale': self.locale,
            'onRender': self.onRender,
            'onChange': self.onChange,
            'onShow': self.onShow,
            'onBeforeShow': self.onBeforeShow,
            'onHide': self.onHide,
            }
        return j01DatePickerJavaScript(self.j01DatePickerExpression, data)

    def update(self):
        """Will setup the script attribute."""
        # setup formatter pattern given from request via converter
        converter = zope.component.queryMultiAdapter((self.field, self),
            z3c.form.interfaces.IDataConverter)
        self.pattern = converter.formatter.getPattern()
        # update widget and converter which uses our own formatter pattern
        super(DatePickerWidget, self).update()


def getDatePickerWidget(field, request):
    """IFieldWidget factory for ItemsWidget."""
    return z3c.form.widget.FieldWidget(field, DatePickerWidget(request))


def getStartDatePickerWidget(field, request):
    """IFieldWidget factory for ItemsWidget."""
    # this widget uses the default timeAppendix settings '00:00:00'
    # and prevents selecting previous dates
    widget = DatePickerWidget(request)
    widget.skipPastDates = True
    return z3c.form.widget.FieldWidget(field, widget)


def getEndDatePickerWidget(field, request):
    """IFieldWidget factory for ItemsWidget."""
    # this widget uses the default timeAppendix settings '23:59:59'
    # and prevents selecting previous dates
    widget = DatePickerWidget(request)
    widget.timeAppendix = '23:59:59'
    widget.skipPastDates = True
    return z3c.form.widget.FieldWidget(field, widget)
