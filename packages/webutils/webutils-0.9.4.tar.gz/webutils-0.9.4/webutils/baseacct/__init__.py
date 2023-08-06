from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.forms import AuthenticationForm
from forms import ResetForm, PasswordChangeForm
from webutils.djtools.easyconfig import EasyConfig


class Config(object):
    ''' Base config class to easily pass forms, etc. to 
        baseacct views.
    '''
    config = EasyConfig('webutils.baseacct.Config', 'BASEACCT_CONFIG')
    
    def get_login_form(self):
        return self.config.get_object('get_login_form', AuthenticationForm)
    
    def get_login_url(self):
        # Defaults to /accounts/login/ - Ugly!
        return self.config.get_object(
            'get_login_url',
            getattr(settings, 'LOGIN_URL', '/accounts/login/'),
        )
    
    def get_reset_form(self):
        return self.config.get_object('get_reset_form', ResetForm)
    
    def get_profile_model(self):
        if not hasattr(settings, 'AUTH_PROFILE_MODULE'):
            raise ImproperlyConfigured(
                'The "AUTH_PROFILE_MODULE" setting MUST be set to use ' + \
                'this method. Please add it to your projects settings.py'
            )
        return self.config.get_object('get_profile_model', None)
    
    def get_password_change_redirect(self):
        return self.config.get_object('get_password_change_redirect', None)
    
    def get_password_change_form(self):
        return self.config.get_object(
            'get_password_change_form',
            PasswordChangeForm,
        )