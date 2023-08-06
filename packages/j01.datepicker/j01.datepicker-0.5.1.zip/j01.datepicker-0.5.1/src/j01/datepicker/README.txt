=================
DatePicker Widget
=================

This package provides two datepicker based widgets. One can be used for 
IDatetime fields and the other for IDate fields.


DatePickerWidget
----------------

As for all widgets, the DatePickerWidget must provide the new ``IWidget``
interface:

  >>> import zope.schema
  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form.interfaces import IWidget
  >>> from z3c.form.interfaces import INPUT_MODE
  >>> from z3c.form.converter import FieldWidgetDataConverter
  >>> from j01.datepicker import interfaces
  >>> from j01.datepicker.converter import DatePickerConverter
  >>> from j01.datepicker.widget import DatePickerWidget

  >>> verifyClass(IWidget, DatePickerWidget)
  True

The widget can be instantiated NOT only using the request like other widgets,
we need an additional schema field because our widget uses a converter for
find the right date formatter pattern.Let's setup a schema field now:

  >>> date = zope.schema.Date(
  ...     title=u"date",
  ...     description=u"date")

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()

  >>> widget = DatePickerWidget(request)
  >>> widget.field = date

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget.id'
  >>> widget.name = 'widget.date'

We also need to register the template for the widget:

  >>> import zope.component
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from z3c.form.widget import WidgetTemplateFactory

  >>> import os
  >>> import j01.datepicker
  >>> def getPath(filename):
  ...     return os.path.join(os.path.dirname(j01.datepicker.__file__),
  ...     filename)

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('input.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IDatePickerWidget),
  ...     IPageTemplate, name=INPUT_MODE)

And we need our DatePickerConverter date converter:

  >>> zope.component.provideAdapter(FieldWidgetDataConverter)
  >>> zope.component.provideAdapter(DatePickerConverter)

If we render the widget we get a simple input element. The given input element
id called ``j01DatePickerWidget`` will display a nice date picker if you click
on it and load the selected date into the given input element with the id
``j01DatePickerWidget``:

  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="widget.id" name="widget.date" class="j01DatePickerWidget" value="" />
  <BLANKLINE>
  <script type="text/javascript">
    $(document).ready(function(){
      $("#widget\\.id").DatePicker({
      flat: false,
      onRender: function(date) {
          var now = new Date();
          var clsName = date.valueOf() == now.valueOf() ? 'datepickerCurrent' : false
              return {className: clsName}
      },
      onShow: function(){return true;},
      format: 'm.d.Y',
      locale: {
          daysMin: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
          months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
          days: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
          daysShort: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          weekMin: 'wk',
          monthsShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']},
      starts: 1,
      view: 'days',
      calendars: 1,
      onHide: function(){return true;},
      next: '&rsaquo;',
      current: '...',
      onBeforeShow: function(){
          var val = $('#widget\\.id').val();
          if (val) {
              $('#widget\\.id').DatePickerSetDate(val, false);
          }
      },
      eventName: 'click',
      onChange: function(formated, dates){
          $('#widget\\.id').val(formated);
          $('#widget\\.id').DatePickerHide();
      },
      mode: 'single',
      date: $('#widget\\.id').val(),
      position: 'bottom',
      prev: '&lsaquo;',
      lastSel: false});
    });
  </script>
  <BLANKLINE>

A value will get rendered as simple text input:

  >>> widget.value = '24.02.1969'
  >>> print widget.render()
  <input type="text" id="widget.id" name="widget.date" class="j01DatePickerWidget" value="24.02.1969" />
  <BLANKLINE>
  <script type="text/javascript">
    $(document).ready(function(){
      $("#widget\\.id").DatePicker({
      flat: false,
      onRender: function(date) {
          var now = new Date();
          var clsName = date.valueOf() == now.valueOf() ? 'datepickerCurrent' : false
              return {className: clsName}
      },
      onShow: function(){return true;},
      format: 'm.d.Y',
      locale: {
          daysMin: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
          months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
          days: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
          daysShort: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          weekMin: 'wk',
          monthsShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']},
      starts: 1,
      view: 'days',
      calendars: 1,
      onHide: function(){return true;},
      next: '&rsaquo;',
      current: '...',
      onBeforeShow: function(){
          var val = $('#widget\\.id').val();
          if (val) {
              $('#widget\\.id').DatePickerSetDate(val, false);
          }
      },
      eventName: 'click',
      onChange: function(formated, dates){
          $('#widget\\.id').val(formated);
          $('#widget\\.id').DatePickerHide();
      },
      mode: 'single',
      date: $('#widget\\.id').val(),
      position: 'bottom',
      prev: '&lsaquo;',
      lastSel: false});
    });
  </script>
  <BLANKLINE>

Let's now make sure that we can extract user entered data from a widget:

  >>> widget.request = TestRequest(form={'widget.date': '24.02.1969'})
  >>> widget.update()
  >>> widget.extract()
  '24.02.1969'


If nothing is found in the request, the default is returned:

  >>> widget.request = TestRequest()
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>
