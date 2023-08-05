from __future__ import unicode_literals

from cgi import escape

from wtforms.compat import text_type, string_types, iteritems
from wtforms.widgets import (CheckboxInput, FileInput, HiddenInput, ListWidget, PasswordInput,
                             RadioInput, Select, SubmitInput, TableWidget, TextArea, TextInput, Option)
from wtforms.widgets.core import html_params, HTMLString
from ..validators import get_validation_str

__all__ = (
'DojoInput', 'DojoTextInput', 'DojoValidationTextBox', 'DojoDateTextBox', 'DojoTimeTextBox',
'DojoPasswordBox', 'DojoTextArea', 'DojoSimpleTextArea', 'DojoNumbertextBox', 'DojoNumberSpinner',
'DojoFilteringSelect', 'DojoMultiSelect', 'DojoCheckBox'
)


class DojoInput(object):
    """
    Render a basic ``<input>`` field.

    This is used as the basis for most of the other input fields.

    By default, the `_value()` method will be called upon the associated field
    to provide the ``value=`` HTML attribute.
    """
    html_params = staticmethod(html_params)

    def __init__(self, input_type=None, dojo_type=None):
        if input_type is not None:
            self.input_type = input_type

        if dojo_type is not None:
            self.dojo_type = dojo_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        kwargs.setdefault('data-dojo-type', self.dojo_type)

        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return HTMLString('<input %s>' % self.html_params(name=field.name, **kwargs))


class DojoTextBox(DojoInput):
    """
    Render a single-line text input.
    """
    input_type = 'text'
    dojo_type = "dijit/form/TextBox"


class DojoValidationTextBox(DojoInput):
    """
    Render a single-line text input with validation support for WTForms fields.
    """
    input_type = 'text'
    dojo_type = "dijit/form/ValidationTextBox"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        kwargs.setdefault('data-dojo-type', self.dojo_type)

        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        return HTMLString('<input %s %s>' % (get_validation_str(field),
                                             self.html_params(name=field.name, **kwargs)))


class DojoNumberTextBox(DojoValidationTextBox):
    """
    Render a single-line text input that only accepts numbers.
    """
    input_type = 'text'
    dojo_type = "dijit/form/NumberTextBox"


class DojoNumberSpinner(DojoValidationTextBox):
    """
    Render a number spinner to select a value
    """
    #TODO: A way to specify parameters for the NumberSpinner
    input_type = 'text'
    dojo_type = "dijit/form/NumberSpinner"


class DojoDateTextBox(DojoValidationTextBox):
    """
    Render a single-line text input.
    """
    input_type = 'text'
    dojo_type = "dijit/form/DateTextBox"


class DojoTimeTextBox(DojoValidationTextBox):
    """
    Render a single-line text input.
    """
    input_type = 'text'
    dojo_type = "dijit/form/TimeTextBox"


class DojoPasswordBox(DojoValidationTextBox):
    """
    Render a single-line password input.
    """
    input_type = 'password'

    def __init__(self, hide_value=True):
        self.hide_value = hide_value

    def __call__(self, field, **kwargs):
        if self.hide_value:
            kwargs['value'] = ''
        return super(DojoPasswordBox, self).__call__(field, **kwargs)


class DojoTextArea(DojoInput):
    """
    Renders a multi-line text area that automatically expands when more content is added to it.

    `rows` and `cols` ought to be passed as keyword args when rendering.
    """

    dojo_type = "dijit/form/Textarea"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('data-dojo-type', self.dojo_type)
        return HTMLString('<textarea %s %s>%s</textarea>' % (html_params(name=field.name, **kwargs),
                                                             get_validation_str(field),
                                                             escape(text_type(field._value()))))


class DojoSimpleTextArea(DojoInput):
    """
    Renders a multi-line text area.

    `rows` and `cols` ought to be passed as keyword args when rendering.
    """

    dojo_type = "dijit/form/SimpleTextarea"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('data-dojo-type', self.dojo_type)
        return HTMLString('<textarea %s %s>%s</textarea>' % (html_params(name=field.name, **kwargs),
                                                             get_validation_str(field),
                                                             escape(text_type(field._value()))))


class DojoCheckBox(DojoInput):
    """
    Render a checkbox.

    The ``checked`` HTML attribute is set if the field's data is a non-false value.
    """
    input_type = 'checkbox'
    dojo_type = "dijit/form/CheckBox"

    def __call__(self, field, **kwargs):
        if getattr(field, 'checked', field.data):
            kwargs['checked'] = True
        return super(DojoCheckBox, self).__call__(field, **kwargs)


#class DojoRadioButton(DojoInput):
#    """
#    Render a single radio button.
#
#    This widget is most commonly used in conjunction with ListWidget or some
#    other listing, as singular radio buttons are not very useful.
#    """
#    input_type = 'radio'
#
#    def __call__(self, field, **kwargs):
#        if field.checked:
#            kwargs['checked'] = True 
#        return super(RadioInput, self).__call__(field, **kwargs)

#
#class FileInput(object):
#    """
#    Renders a file input chooser field.
#    """
#
#    def __call__(self, field, **kwargs):
#        kwargs.setdefault('id', field.id)
#        value = field._value()
#        if value:
#            kwargs.setdefault('value', value)
#        return HTMLString('<input %s>' % html_params(name=field.name, type='file', **kwargs))
#
#
#class SubmitInput(Input):
#    """
#    Renders a submit button.
#
#    The field's label is used as the text of the submit button instead of the
#    data on the field.
#    """
#    input_type = 'submit'
#
#    def __call__(self, field, **kwargs): 
#        kwargs.setdefault('value', field.label.text)
#        return super(SubmitInput, self).__call__(field, **kwargs)
#
#


class DojoFilteringSelect(Select):
    """
    Renders a Dojo Filtering Select widget.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected)`.
    """
    dojo_type = "dijit/form/FilteringSelect"

    def __init__(self, input_type=None, dojo_type=None):

        if dojo_type is not None:
            self.dojo_type = dojo_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('data-dojo-type', self.dojo_type)

        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected in field.iter_choices():
            html.append(self.render_option(val, label, selected))
        html.append('</select>')
        return HTMLString(''.join(html))


class DojoMultiSelect(DojoFilteringSelect):
    """
    Renders a Dojo Multi Select widget.

    The `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected)`.
    """

    dojo_type = "dijit/form/MultiSelect"
