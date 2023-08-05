'''Implementation of core ew widgets in terms of Jinja2 templates
'''
from jinja2 import escape

from webhelpers.html import literal

from . import fields
from . import select
from . import forms
from . import widget
from . import resource
from .render import Snippet, File

BOOLEAN_ATTRS=set([
        'checked',
        'disabled',
        'readonly',
        'multiple',
        'selected',
        'nohref',
        'ismap',
        'declare',
        'defer'])

def _escape(s):
    try:
        return s.__html__()
    except:
        pass
    if isinstance(s, str):
        return escape(unicode(s, 'utf-8'))
    else:
        return escape(s)

def _attr(k,v):
    if k.lower() in BOOLEAN_ATTRS:
        return _escape(k)
    else:
        return '%s="%s"' % (
            _escape(k), _escape(v)) 

class _Jinja2Widget(fields.FieldWidget):

    def j2_attrs(self, *attrdicts):
        attrdict={}
        for ad in attrdicts:
            if ad:
                attrdict.update(ad)
        result = [
            _attr(k,v)
            for k,v in sorted(attrdict.items())
            if v is not None ]
        return literal(' '.join(result))

#################
## Overrides from ew.fields
#################

class InputField(fields.InputField, _Jinja2Widget):
    template=Snippet('''<input {{widget.j2_attrs({
    'id':id,
    'type':field_type,
    'name':rendered_name,
    'class':css_class,
    'readonly':readonly,
    'value':value},
    attrs)}}>''', 'jinja2')

class HiddenField(fields.HiddenField, _Jinja2Widget):
    template=InputField.template

class FileField(fields.FileField, _Jinja2Widget):
    # same as above, but no "value"
    template=Snippet('''<input {{widget.j2_attrs({
    'id':id,
    'type':field_type,
    'name':rendered_name,
    'class':css_class,
    'readonly':readonly},
    attrs)}}>''', 'jinja2')

class CompoundField(fields.CompoundField, _Jinja2Widget):
    template=InputField.template

class FieldSet(fields.FieldSet, _Jinja2Widget):
    template=File('ew.templates.jinja2.field_set', 'jinja2')

class RowField(fields.RowField, _Jinja2Widget):
    template=File('ew.templates.jinja2.row_field', 'jinja2')

class RepeatedField(fields.RepeatedField, _Jinja2Widget):
    template=File('ew.templates.jinja2.repeated_field', 'jinja2')

class TableField(fields.TableField, _Jinja2Widget):
    template=File('ew.templates.jinja2.table_field', 'jinja2')
TableField.RowField=RowField

class TextField(fields.TextField, _Jinja2Widget): 
    template=InputField.template

class PasswordField(fields.PasswordField, _Jinja2Widget): 
    template=InputField.template

class EmailField(fields.EmailField, _Jinja2Widget):
    template=InputField.template

class NumberField(fields.NumberField, _Jinja2Widget):
    template=InputField.template

class IntField(fields.IntField, _Jinja2Widget):
    template=InputField.template

class DateField(fields.DateField, _Jinja2Widget):
    template=InputField.template

class TimeField(fields.TimeField, _Jinja2Widget):
    template=InputField.template

class TextArea(fields.TextArea, _Jinja2Widget):
    template=Snippet('''<textarea {{widget.j2_attrs({
    'id':id,
    'name':rendered_name,
    'class':css_class,
    'readonly':readonly},
    attrs)}}>{% if value %}{{value}}{% endif %}</textarea>''', 'jinja2')

class Checkbox(fields.Checkbox, _Jinja2Widget):
    template=File('ew.templates.jinja2.checkbox', 'jinja2')

class SubmitButton(fields.SubmitButton, _Jinja2Widget):
    template=Snippet('''<input {{widget.j2_attrs({
    'type':'submit',
    'name':rendered_name,
    'value':label,
    'class':css_class},
    attrs)}}>''', 'jinja2')

class HTMLField(fields.HTMLField, _Jinja2Widget):
    template=Snippet('''{% if text %}{{widget.expand(text)|safe}}
    {%- elif value %}{{value | safe}}{% endif %}''', 'jinja2')

class LinkField(fields.LinkField, _Jinja2Widget):
    template=Snippet('''<a href="{{widget.expand(href)}}" {{widget.j2_attrs(attrs)}}>
    {%- if text == None %}{{widget.expand(label)}}
    {%- else %}{{widget.expand(text)}}{% endif %}</a>''',
                     'jinja2')

#################
## Overrides from ew.select
#################

class SelectField(select.SelectField, _Jinja2Widget):
    template=File('ew.templates.jinja2.select_field', 'jinja2')

class SingleSelectField(select.SingleSelectField, _Jinja2Widget):
    template=SelectField.template

class MultiSelectField(select.MultiSelectField, _Jinja2Widget):
    template=SelectField.template

class Option(select.Option, _Jinja2Widget):
    template=Snippet('''<option {{widget.j2_attrs({
      'value':html_value,
      'selected':selected and 'selected' or None})}}>
     {{label}}</option>''', 'jinja2')

class CheckboxSet(select.CheckboxSet, _Jinja2Widget):
    template=File('ew.templates.jinja2.checkbox_set', 'jinja2')

#################
## Overrides from ew.forms
#################

class SimpleForm(forms.SimpleForm, _Jinja2Widget):
    template=File('ew.templates.jinja2.simple_form', 'jinja2')
SimpleForm.SubmitButton=SubmitButton

#################
## Overrides from ew.resource
#################

class JSLink(resource.JSLink):
    class WidgetClass(_Jinja2Widget): 
        template=Snippet('<script type="text/javascript" src="{{widget.href}}"></script>',
                         'jinja2')

class CSSLink(resource.CSSLink):
    class WidgetClass(_Jinja2Widget): 
        template=Snippet('''<link rel="stylesheet"
                type="text/css"
                href="{{widget.href}}"
                {{widget.j2_attrs(widget.attrs)}}>''', 'jinja2')

class JSScript(resource.JSScript):
    class WidgetClass(_Jinja2Widget): 
        template=Snippet(
            '<script type="text/javascript">{{widget.text}}</script>',
            'jinja2')

class CSSScript(resource.CSSScript):
    class WidgetClass(_Jinja2Widget): 
        template=Snippet('<style>{{widget.text}}</style>', 'jinja2')

class GoogleAnalytics(resource.GoogleAnalytics):
    class WidgetClass(_Jinja2Widget): 
        template=File('ew.templates.jinja2.google_analytics', 'jinja2')
