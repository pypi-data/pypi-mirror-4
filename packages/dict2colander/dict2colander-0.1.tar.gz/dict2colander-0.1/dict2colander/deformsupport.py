# Copyright (C) 2012, Peter Facka, David Nemcok
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import deform
import deform.widget
import colander
from dict2colander import SchemaBuilder, Default


class CommonRequirements(colander.Tuple):
    resource = colander.SchemaNode(colander.String(), missing=Default)
    version = colander.SchemaNode(colander.String(), missing=Default)
    

class MoneyInputOptionsSchema(colander.Mapping):
    
    symbol = colander.SchemaNode(colander.String(), missing=Default)
    showSymbol = colander.SchemaNode(colander.Boolean(), missing=Default)
    symbolStay = colander.SchemaNode(colander.Boolean(), missing=Default)
    thousands = colander.SchemaNode(colander.String(), missing=Default)
    decimal = colander.SchemaNode(colander.String(), missing=Default)
    precision = colander.SchemaNode(colander.Integer(), missing=Default)
    defaultZero = colander.SchemaNode(colander.Boolean(), missing=Default)
    allowZero = colander.SchemaNode(colander.Boolean(), missing=Default)
    allowNegative = colander.SchemaNode(colander.Boolean(), missing=Default)


class ChoiceValues(colander.Tuple):
    return_value = colander.SchemaNode(colander.Boolean())
    display_value = colander.SchemaNode(colander.String())


class CommonKwArgsSchema(colander.MappingSchema):
    
    hidden = colander.SchemaNode(colander.Boolean(), missing=Default)
    category = colander.SchemaNode(colander.String(), missing=Default)
    error_class = colander.SchemaNode(colander.String(), missing=Default)
    css_class = colander.SchemaNode(colander.String(), missing=Default)
    requiremets = colander.SchemaNode(colander.Sequence(), CommonRequirements(), 
    missing=Default)
    #TODO: test requirements field


class InputKwArgsSchema(CommonKwArgsSchema):

    size = colander.SchemaNode(colander.Integer(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(),
        missing=Default)


class TextInputKwArgsSchema(InputKwArgsSchema):
    
    template = colander.SchemaNode(colander.String(), missing=Default)

    strip = colander.SchemaNode(colander.Boolean(), missing=Default)
    mask = colander.SchemaNode(colander.String(), missing=Default)
    mask_placeholder = colander.SchemaNode(colander.String(), missing=Default)


class MoneyInputKwArgsSchema(InputKwArgsSchema):

    template = colander.SchemaNode(colander.String(), missing=Default)
    options = colander.SchemaNode(MoneyInputOptionsSchema(), missing=Default)
    #TODO:test options mapping schema


class AutocompleteInputKwArgsSchema(InputKwArgsSchema):
    
    template = colander.SchemaNode(colander.String(), 
        missing=Default)
    readonly_template = colander.SchemaNode(colander.String(),
        missing=Default)

    strip = colander.SchemaNode(colander.Boolean(), missing=Default)
    values = colander.SchemaNode(colander.Sequence(),colander.String(), 
        missing=Default) #TODO: chceck if correct

    min_length = colander.SchemaNode(colander.Integer(), missing=Default)
    delay = colander.SchemaNode(colander.Integer(), missing=Default)


class HiddenKwArgsSchema(CommonKwArgsSchema):

    template = colander.SchemaNode(colander.String(), missing=Default)
 

class TextAreaKwArgsSchema(CommonKwArgsSchema):

    cols = colander.SchemaNode(colander.Integer(), missing=Default)
    rows = colander.SchemaNode(colander.Integer(), missing=Default)
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly = colander.SchemaNode(colander.String(),
       missing=Default)
    strip = colander.SchemaNode(colander.Boolean(), missing=Default)
    

class RichTextKwArgsSchema(CommonKwArgsSchema):
    
    height = colander.SchemaNode(colander.Integer(), missing=Default)
    readonly = colander.SchemaNode(colander.String(),
       missing=Default)
    delayed_load = colander.SchemaNode(colander.Boolean(), missing=Default)
    strip = colander.SchemaNode(colander.Boolean(), missing=Default)
    theme = colander.SchemaNode(colander.String(), missing=Default)
    height = colander.SchemaNode(colander.Integer(), missing=Default)


class CheckboxKwArgsSchema(CommonKwArgsSchema):
    true_val = colander.SchemaNode(colander.Boolean(), missing=Default)
    false_val = colander.SchemaNode(colander.Boolean(), missing=Default)
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(),
       missing=Default)
       

class CheckedInputKwArgsSchema(CommonKwArgsSchema):
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(),
       missing=Default)
    size = colander.SchemaNode(colander.Integer(), missing=Default)
    mismatch_message = colander.SchemaNode(colander.String(), missing=Default)
    mask = colander.SchemaNode(colander.String(), missing=Default)
    mask_placeholder = colander.SchemaNode(colander.String(), missing=Default)


class CheckedPasswordKwArgsSchema(CommonKwArgsSchema):
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)
    size = colander.SchemaNode(colander.Integer(), missing=Default)


class CheckboxChoiceKwArgsSchema(CommonKwArgsSchema):
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)
    values = colander.SchemaNode(ChoiceValues, missing=Default)
    null_value = colander.SchemaNode(colander.String(), missing=Default)
    #TODO:test for values 
    

#class OptGroupKwArgsSchema(CommonKwArgsSchema):
#    label = colander.SchemaNode(colander.String(), missing=Default)
#    #TODO: options =

    
class SelectKwArgsSchema(CommonKwArgsSchema):
    #TODO: values =
    size = colander.SchemaNode(colander.Integer(), missing=Default)
    null_value = colander.SchemaNode(colander.String(), missing=Default)
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)
    optgroup_class = colander.SchemaNode(colander.String(), missing=Default)
    #TODO log_label


class RadioChoiceKwArgsSchema(CommonKwArgsSchema):
    values = colander.SchemaNode(ChoiceValues, missing=Default)
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)
    null_value = colander.SchemaNode(colander.String(), missing=Default)
    #TODO:test for values 


class MappingKwArgsSchema(CommonKwArgsSchema):
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)
    item_template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_item_template = colander.SchemaNode(colander.String(), missing=Default)
       

class SequenceKwArgsSchema(CommonKwArgsSchema):
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)
    item_template = colander.SchemaNode(colander.String(), missing=Default)
    add_subitem_text_template = colander.SchemaNode(colander.String(), missing=Default)
    render_initial_item = colander.SchemaNode(colander.Boolean(), missing=Default)
    min_len = colander.SchemaNode(colander.Integer(), missing=Default)
    max_len = colander.SchemaNode(colander.Integer(), missing=Default)
    

class FileUploadKwArgsSchema(CommonKwArgsSchema):
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)
    size = colander.SchemaNode(colander.Integer(), missing=Default)
    

class DateInputKwArgsSchema(CommonKwArgsSchema):
    #TODO:options
    size = colander.SchemaNode(colander.Integer(), missing=Default)
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)


class DateTimeInputKwArgsSchema(CommonKwArgsSchema):
    #TODO:options
    size = colander.SchemaNode(colander.Integer(), missing=Default)
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)


class DatePartsKwArgsSchema(CommonKwArgsSchema):
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)
    size = colander.SchemaNode(colander.Integer(), missing=Default)
    assume_y2k = colander.SchemaNode(colander.Boolean(), missing=Default)


class FormKwArgsSchema(CommonKwArgsSchema):
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)
    item_template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_item_template = colander.SchemaNode(colander.String(), missing=Default)
    
    
class TextAreaCSVKwArgsSchema(CommonKwArgsSchema):
    cols = colander.SchemaNode(colander.Integer(), missing=Default)
    rows = colander.SchemaNode(colander.Integer(), missing=Default)
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)

   
class TextInputCSVKwArgsSchema(CommonKwArgsSchema):
    template = colander.SchemaNode(colander.String(), missing=Default)
    readonly_template = colander.SchemaNode(colander.String(), missing=Default)
    size = colander.SchemaNode(colander.Integer(), missing=Default)
    


class DeformSchemaBuilder(SchemaBuilder):
    
    def __init__(self):
        super(DeformSchemaBuilder,self).__init__()

        self.add_widget('TextInput', deform.widget.TextInputWidget, None,
            TextInputKwArgsSchema)

        self.add_widget('MoneyInput', deform.widget.MoneyInputWidget, None,
            MoneyInputKwArgsSchema)

        self.add_widget('AutocompleteInput', 
            deform.widget.AutocompleteInputWidget, None, 
            AutocompleteInputKwArgsSchema)

        self.add_widget('Hidden', deform.widget.HiddenWidget, None,
            HiddenKwArgsSchema)

        self.add_widget('TextArea', deform.widget.TextAreaWidget, None,
            TextAreaKwArgsSchema)

        self.add_widget('RichText', deform.widget.RichTextWidget, None,
            RichTextKwArgsSchema)

        self.add_widget('Checkbox', deform.widget.CheckboxWidget, None,
            CheckboxKwArgsSchema)

        self.add_widget('CheckedInput', deform.widget.CheckedInputWidget, None,
            CheckedInputKwArgsSchema)

        self.add_widget('CheckedPassword', deform.widget.CheckedPasswordWidget, None,
            CheckedPasswordKwArgsSchema)

        self.add_widget('CheckboxChoice', deform.widget.CheckboxChoiceWidget, None,
            CheckboxChoiceKwArgsSchema)

        self.add_widget('Select', deform.widget.SelectWidget, None,
            SelectKwArgsSchema)

        self.add_widget('RadioChoice', deform.widget.RadioChoiceWidget, None,
            RadioChoiceKwArgsSchema)

        self.add_widget('Mapping', deform.widget.MappingWidget, None,
            MappingKwArgsSchema)

        self.add_widget('Sequence', deform.widget.SequenceWidget, None,
            SequenceKwArgsSchema)

        self.add_widget('FileUpload', deform.widget.FileUploadWidget, None,
            FileUploadKwArgsSchema)

        self.add_widget('DateInput', deform.widget.DateInputWidget, None,
            DateInputKwArgsSchema)

        self.add_widget('DateParts', deform.widget.DatePartsWidget, None,
            DatePartsKwArgsSchema)

        self.add_widget('Form', deform.widget.FormWidget, None,
            FormKwArgsSchema)

        self.add_widget('TextAreaCSV', deform.widget.TextAreaCSVWidget, None,
            TextAreaCSVKwArgsSchema)

        self.add_widget('TextInputCSV', deform.widget.TextInputCSVWidget, None,
            TextInputCSVKwArgsSchema)


