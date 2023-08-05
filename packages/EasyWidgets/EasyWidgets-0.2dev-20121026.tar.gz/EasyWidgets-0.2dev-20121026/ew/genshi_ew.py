'''Implementation of core ew widgets in terms of genshi templates
'''
from . import fields
from . import select
from . import forms
from .render import Snippet, File

class InputField(fields.InputField):
    template=Snippet('''<input type="$field_type" name="$rendered_name"
    class="$css_class" readonly="${readonly or None}" py:attrs="attrs"
    value="$value"/>''', 'genshi')

class FileField(fields.FileField):
    # same as above, but no "value"
    template=Snippet('''<input type="$field_type" name="$rendered_name"
    class="$css_class" readonly="${readonly or None}" py:attrs="attrs"/>''',
    'genshi')

class HiddenField(fields.HiddenField):
    template=InputField.template

class CompoundField(fields.CompoundField):
    template=InputField.template

class FieldSet(fields.FieldSet):
    template=File('ew.templates.genshi.field_set', 'genshi')

class RowField(fields.RowField):
    template=File('ew.templates.genshi.row_field', 'genshi')

class RepeatedField(fields.RepeatedField):
    template=File('ew.templates.genshi.repeated_field', 'genshi')

class TableField(fields.TableField):
    template=File('ew.templates.genshi.table_field', 'genshi')

class TextField(fields.TextField): 
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
    template=Snippet('''<textarea name="$rendered_name"
            class="$css_class" readonly="${readonly or None}"
            py:attrs="attrs">$value</textarea>''', 'genshi')

class Checkbox(fields.Checkbox):
    template=File('ew.templates.genshi.checkbox', 'genshi')

class SubmitButton(fields.SubmitButton):
    template=Snippet('''<input type="submit" name="$rendered_name"
       class="$css_class" readonly="${readonly or None}"
       py:attrs="attrs" value="$label"/>''', 'genshi')

class SelectField(select.SelectField):
    template=File('ew.templates.genshi.select_field', 'genshi')

class SingleSelectField(select.SingleSelectField):
    template=SelectField.template

class MultiSelectField(select.MultiSelectField):
    template=SelectField.template

class Option(select.Option):
    template=Snippet('''<option value="$html_value"
     selected="${selected and 'selected' or None}"
     >$label</option>''', 'genshi')

class CheckboxSet(select.CheckboxSet):
    template=File('ew.templates.genshi.checkbox_set', 'genshi')

class SimpleForm(forms.SimpleForm):
    template=File('ew.templates.genshi.simple_form', 'genshi')
    
