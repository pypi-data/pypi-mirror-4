'''Implementation of core ew widgets in terms of kajiki-html4 templates
'''
from . import fields
from . import select
from . import forms
from . import widget
from . import resource
from .render import Snippet, File

#################
## Overrides from ew.fields
#################

class InputField(fields.InputField):
    template=Snippet('''<input id="$id" type="$field_type" name="$rendered_name"
    class="$css_class" readonly="${readonly or None}" value="$value"
    py:attrs="attrs"/>''', 'kajiki-html4')

class FileField(fields.FileField):
    # same as above, but no "value"
    template=Snippet('''<input id="$id" type="$field_type" name="$rendered_name"
    class="$css_class" readonly="${readonly or None}" 
    py:attrs="attrs"/>''', 'kajiki-html4')

class HiddenField(fields.HiddenField):
    template=InputField.template

class CompoundField(fields.CompoundField):
    template=InputField.template

class FieldSet(fields.FieldSet):
    template=File('ew.templates.kajiki.field_set', 'kajiki-html4')

class RowField(fields.RowField):
    template=File('ew.templates.kajiki.row_field', 'kajiki-html4')

class RepeatedField(fields.RepeatedField):
    template=File('ew.templates.kajiki.repeated_field', 'kajiki-html4')

class TableField(fields.TableField):
    template=File('ew.templates.kajiki.table_field', 'kajiki-html4')
TableField.RowField=RowField

class TextField(fields.TextField): 
    template=InputField.template

class PasswordField(fields.PasswordField): 
    template=InputField.template

class EmailField(fields.EmailField):
    template=InputField.template

class NumberField(fields.NumberField):
    template=InputField.template

class IntField(fields.IntField):
    template=InputField.template

class DateField(fields.DateField):
    template=InputField.template

class TimeField(fields.TimeField):
    template=InputField.template

class TextArea(fields.TextArea):
    template=Snippet('''<textarea id="$id" name="$rendered_name"
            class="$css_class" readonly="${readonly or None}"
            py:attrs="attrs">$value</textarea>''', 'kajiki-html4')

class Checkbox(fields.Checkbox):
    template=File('ew.templates.kajiki.checkbox', 'kajiki-html4')

class SubmitButton(fields.SubmitButton):
    template=Snippet('''<input type="submit" name="$rendered_name"
       class="$css_class" readonly="${readonly or None}"
       py:attrs="attrs" value="$label"/>''', 'kajiki-html4')

class HTMLField(fields.HTMLField):
    template=Snippet('''<div py:strip="True"><py:if test="text"
    >${literal(widget.expand(text))}</py:if><py:if
    test="not text and unicode(value)">${literal(value)}</py:if></div>''',
                     'kajiki-html4')

class LinkField(fields.LinkField):
    template=Snippet('''<a href="${widget.expand(href)}" py:attrs="attrs"><py:if
    test="text is None">${widget.expand(label)}</py:if><py:if
    test="text is not None">${widget.expand(text)}</py:if></a>''',
                     'kajiki-html4')

#################
## Overrides from ew.select
#################

class SelectField(select.SelectField):
    template=File('ew.templates.kajiki.select_field', 'kajiki-html4')

class SingleSelectField(select.SingleSelectField):
    template=SelectField.template

class MultiSelectField(select.MultiSelectField):
    template=SelectField.template

class Option(select.Option):
    template=Snippet('''<option value="$html_value"
     selected="${selected and 'selected' or None}"
     >$label</option>''', 'kajiki-html4')

class CheckboxSet(select.CheckboxSet):
    template=File('ew.templates.kajiki.checkbox_set', 'kajiki-html4')

#################
## Overrides from ew.forms
#################

class SimpleForm(forms.SimpleForm):
    template=File('ew.templates.kajiki.simple_form', 'kajiki-html4')
SimpleForm.SubmitButton=SubmitButton
    
#################
## Overrides from ew.resource
#################

class JSLink(resource.JSLink):
    class WidgetClass(widget.Widget):
        template=Snippet('<script type="text/javascript" src="$widget.href"/>',
                         'kajiki-html4')

class CSSLink(resource.CSSLink):
    file_type='css'
    class WidgetClass(widget.Widget):
        template=Snippet('''<link rel="stylesheet"
            type="text/css"
            href="${widget.href}"
            py:attrs="widget.attrs"/>''', 'kajiki-html4')

class JSScript(resource.JSScript):
    class WidgetClass(widget.Widget):
        template=Snippet(
            '<script type="text/javascript">$widget.text</script>',
            'kajiki-html4')

class CSSScript(resource.CSSScript):
    class WidgetClass(widget.Widget):
        template=Snippet('<style>$widget.text</style>', 'kajiki-html4')

class GoogleAnalytics(resource.GoogleAnalytics):
    class WidgetClass(widget.Widget):
        template=File('ew.templates.kajiki.google_analytics', 'kajiki-html4')
