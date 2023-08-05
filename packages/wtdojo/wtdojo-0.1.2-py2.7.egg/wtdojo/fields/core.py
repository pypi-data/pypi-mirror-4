from datetime import date, datetime, time
from .. import widgets as dojo_widgets
from wtforms import widgets as wt_widgets
from wtforms.compat import text_type, izip
from wtforms.fields import (Field, StringField, TextField, TextAreaField, BooleanField, DateField, DateTimeField,
                            DecimalField, FieldList, FileField, FloatField, FormField, HiddenField, IntegerField,
                            Label, PasswordField, RadioField, SelectField, SelectFieldBase, SelectMultipleField,
                            SubmitField, Flags)

__all__ = (
    'DojoStringField', 'DojoDateField', 'DojoTimeField', 'DojoIntegerField',
    'DojoSelectField', 'DojoSelectMultipleField', 'DojoBooleanField'
)


class DojoStringField(StringField):
    """
    This field is the base for most of the more complicated fields, and
    represents an ``<input type="text">``.
    """
    widget = dojo_widgets.DojoValidationTextBox()


class DojoBooleanField(BooleanField):
    """
    Represents an ``<input type="checkbox">``.
    """
    widget = dojo_widgets.DojoCheckBox()


class DojoDateField(DateTimeField):
    """
    A text field which stores a `datetime.date` matching a format.
    """

    widget = dojo_widgets.DojoDateTextBox()

    def __init__(self, label=None, validators=None, format='%Y-%m-%d', **kwargs):
        super(DojoDateField, self).__init__(label, validators, format, **kwargs)
        self.format = format

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.format) or ''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            try:
                self.data = datetime.strptime(date_str, self.format).date()
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid date value'))


class DojoTimeField(DateTimeField):
    """
    A text field which stores a `datetime.time` matching a format.
    """

    widget = dojo_widgets.DojoTimeTextBox()

    def __init__(self, label=None, validators=None, format='T%H:%M:%S', **kwargs):
        super(DojoTimeField, self).__init__(label, validators, format, **kwargs)
        self.format = format

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.format) or ''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            try:
                self.data = datetime.strptime(date_str, self.format).time()
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid time value'))


class DojoSelectField(SelectField):
    widget = dojo_widgets.DojoFilteringSelect()


class DojoSelectMultipleField(SelectMultipleField):
    """
    No different from a normal select field, except this one can take (and
    validate) multiple choices.  You'll need to specify the HTML `rows`
    attribute to the select field when rendering.
    """
    widget = dojo_widgets.DojoMultiSelect()


class DojoIntegerField(IntegerField):
    """
    A text field, except all input is coerced to an integer.  Erroneous input
    is ignored and will not be accepted as a value.
    """
    widget = dojo_widgets.DojoNumberTextBox()

    def __init__(self, label=None, validators=None, **kwargs):
        super(DojoIntegerField, self).__init__(label, validators, **kwargs)


class DojoDecimalField(DecimalField):
    """
    A text field, except all input is coerced to an decimal.  Erroneous input
    is ignored and will not be accepted as a value.
    """
    widget = dojo_widgets.DojoNumberTextBox()

    def __init__(self, label=None, validators=None, places=2, rounding=None, **kwargs):
        super(DojoDecimalField, self).__init__(label, validators, **kwargs)
        self.places = places
        self.rounding = rounding

#class DecimalField(Field):
#    """
#    A text field which displays and coerces data of the `decimal.Decimal` type.
#
#    :param places:
#        How many decimal places to quantize the value to for display on form.
#        If None, does not quantize value.
#    :param rounding:
#        How to round the value during quantize, for example
#        `decimal.ROUND_UP`. If unset, uses the rounding value from the
#        current thread's context.
#    """
#    widget = widgets.TextInput()
#
#    def __init__(self, label=None, validators=None, places=2, rounding=None, **kwargs):
#        super(DecimalField, self).__init__(label, validators, **kwargs)
#        self.places = places
#        self.rounding = rounding
#
#    def _value(self):
#        if self.raw_data:
#            return self.raw_data[0]
#        elif self.data is not None:
#            if self.places is not None:
#                if hasattr(self.data, 'quantize'):
#                    exp = decimal.Decimal('.1') ** self.places
#                    if self.rounding is None:
#                        quantized = self.data.quantize(exp)
#                    else:
#                        quantized = self.data.quantize(exp, rounding=self.rounding)
#                    return text_type(quantized)
#                else:
#                    # If for some reason, data is a float or int, then format
#                    # as we would for floats using string formatting.
#                    format = '%%0.%df' % self.places
#                    return format % self.data
#            else:
#                return text_type(self.data)
#        else:
#            return ''
#
#    def process_formdata(self, valuelist):
#        if valuelist:
#            try:
#                self.data = decimal.Decimal(valuelist[0])
#            except (decimal.InvalidOperation, ValueError):
#                self.data = None
#                raise ValueError(self.gettext('Not a valid decimal value'))
#
#
#class FloatField(Field):
#    """
#    A text field, except all input is coerced to an float.  Erroneous input
#    is ignored and will not be accepted as a value.
#    """
#    widget = widgets.TextInput()
#
#    def __init__(self, label=None, validators=None, **kwargs):
#        super(FloatField, self).__init__(label, validators, **kwargs)
#
#    def _value(self):
#        if self.raw_data:
#            return self.raw_data[0]
#        elif self.data is not None:
#            return text_type(self.data)
#        else:
#            return ''
#
#    def process_formdata(self, valuelist):
#        if valuelist:
#            try:
#                self.data = float(valuelist[0])
#            except ValueError:
#                self.data = None
#                raise ValueError(self.gettext('Not a valid float value'))


#class RadioField(SelectField):
#    """
#    Like a SelectField, except displays a list of radio buttons.
#
#    Iterating the field will produce subfields (each containing a label as
#    well) in order to allow custom rendering of the individual radio fields.
#    """
#    widget = widgets.ListWidget(prefix_label=False)
#    option_widget = widgets.RadioInput()


#
#

#

#
#class FileField(TextField):
#    """
#    Can render a file-upload field.  Will take any passed filename value, if
#    any is sent by the browser in the post params.  This field will NOT
#    actually handle the file upload portion, as wtforms does not deal with
#    individual frameworks' file handling capabilities.
#    """
#    widget = widgets.FileInput()
#
#
#class HiddenField(TextField):
#    """
#    Represents an ``<input type="hidden">``.
#    """
#    widget = widgets.HiddenInput()
#
#
#class SubmitField(BooleanField):
#    """
#    Represents an ``<input type="submit">``.  This allows checking if a given
#    submit button has been pressed.
#    """
#    widget = widgets.SubmitInput()
