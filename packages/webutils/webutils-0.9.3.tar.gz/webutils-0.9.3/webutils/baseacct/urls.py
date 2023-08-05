from webutils.baseacct import Config
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template
from django.conf.urls.defaults import *


config = Config()

urlpatterns = patterns('webutils.baseacct.views',
    url(r'^login/$',
        auth_views.login, {
            'template_name': 'baseacct/login.html',
            'authentication_form': config.get_login_form(),
        }, name='baseacct-login'),
    url(r'^logout/$',
        auth_views.logout, {
            'template_name': 'baseacct/logout.html',
        }, name='baseacct-logout'),
    url(r'^logout-login/$',
        auth_views.logout_then_login,
        {'login_url': config.get_login_url()},
        name='baseacct-logout-login'),
    url(r'^password_change/$',
        'password_change', {
            'template': 'baseacct/password_change.html',
            'password_change_redirect': config.get_password_change_redirect(),
            'password_change_form': config.get_password_change_form(),
        }, name='baseacct-password-change'),
    url(r'^password_change/done/$',
        direct_to_template, {
            'template': 'baseacct/password_change_done.html',
        }, name='baseacct-password-change-done'),
    url(r'^reset/$',
        'reset', {
            'template': 'baseacct/reset.html',
            'reset_form': config.get_reset_form(),
            'profile_model': config.get_profile_model(),
        }, name='baseacct-reset'),
    url(r'^reset/(?P<key>\w+)/$',
        'reset', {
            'template': 'baseacct/reset_complete.html',
            'reset_form': config.get_reset_form(),
            'profile_model': config.get_profile_model(),
        }, name='baseacct-reset-key'),
)
