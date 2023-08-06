import re
import datetime
from django import forms
from django.forms.util import flatatt
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


class TextInputCCEXP(forms.TextInput):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            if isinstance(value, datetime.datetime):
                value = value.date()

            if isinstance(value, datetime.date):
                final_attrs['value'] = force_unicode(value.strftime('%m/%y'))
            else:
                final_attrs['value'] = force_unicode(value)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class DateFieldCCEXP(forms.DateField):
    default_error_messages = {
        'invalid': u'Please use the format: MM/YY',
    }
    widget = TextInputCCEXP

    def clean(self, value):
        if value in (None, ''):
            raise forms.ValidationError(self.error_messages['required'])
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value

        if re.search('^\d{1,2}/\d{2}$', value):
            month, year = map(int, value.split('/'))
            return datetime.date((2000 + year), month, 1)

        raise forms.ValidationError(self.error_messages['invalid'])