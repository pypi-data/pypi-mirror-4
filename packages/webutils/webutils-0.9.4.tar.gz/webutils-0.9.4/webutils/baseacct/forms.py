from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _


class ResetForm(forms.Form):
    email = forms.EmailField(
        max_length=125,
        label=_('Email Address'),
    )

    def clean_email(self):
        if 'email' in self.cleaned_data:
            email = self.cleaned_data['email']
            if not User.objects.filter(email__iexact=email).count() > 0:
                raise forms.ValidationError(
                    u'There is no account registered to this email address.'
                )
            return email.lower()

        raise forms.ValidationError(u'This field is required.')


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label=_('Old Password'),
        widget=forms.PasswordInput,
    )
    new_password = forms.CharField(
        label=_('New Password'),
        widget=forms.PasswordInput,
    )
    new_password2 = forms.CharField(
        label=_('Confirm New Password'),
        widget=forms.PasswordInput,
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
    
    def clean_old_password(self):
        if 'old_password' in self.cleaned_data:
            oldpw = self.cleaned_data['old_password']
            if not self.user.check_password(oldpw):
                raise forms.ValidationError(_(
                    'Your old password was entered incorrectly. ' + \
                    'Please enter it again.'
                ))
            return oldpw
        raise forms.ValidationError(_('This field is required.'))
    
    def clean_new_password2(self):
        if 'new_password2' in self.cleaned_data:
            pw1 = self.cleaned_data.get('new_password')
            pw2 = self.cleaned_data.get('new_password2')
            if pw1 != pw2:
                raise forms.ValidationError(_(
                    'The two password fields didn\'t match.'
                ))
            return pw2
        raise forms.ValidationError(_('This field is required.'))
    
    def save(self):
        self.user.set_password(self.cleaned_data['new_password'])
        self.user.save()