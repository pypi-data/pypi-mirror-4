import re
from django import forms
from django.forms.util import ErrorList
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper

tagTailPattern = re.compile(r' ?/>')

class Form(forms.Form):
    def __init__(self, *args, **kwargs):
        # Remove suffix
        kwargs['label_suffix'] = ''
        kwargs['error_class'] = DivErrorList
        super(Form, self).__init__(*args, **kwargs)
        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False

    error_css_class = 'error'
    required_css_class = 'required'

    def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        # HTML5-lize
        output = super(Form, self)._html_output(normal_row, error_row, row_ender, help_text_html,
            errors_on_separate_row)
        output = re.sub(tagTailPattern, '>', output)
        return mark_safe(output)

    def as_divs(self):
        """Returns this form rendered as HTML <div>s"""
        return self._html_output(
            normal_row=u'<div%(html_class_attr)s>\n    <div class="name">%(label)s</div>\n    <div class="field">%(field)s</div>%(help_text)s\n</div>',
            error_row=u'<div class="error">%s</div>',
            row_ender='</div>',
            help_text_html=u'\n    <div class="helptext">%s</div>',
            errors_on_separate_row=True)


class DivErrorList(ErrorList):
    def __unicode__(self):
        return self.as_divs()

    def as_divs(self):
        if not self: return u''
        return mark_safe(
            u'<div class="errorlist">%s</div>' % ''.join([u'<div class="erroritem">%s</div>' % e for e in self]))