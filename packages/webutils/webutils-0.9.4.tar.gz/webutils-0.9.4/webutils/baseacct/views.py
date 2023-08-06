from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import loader, RequestContext
from django.shortcuts import render_to_response, redirect
from webutils.baseacct import Config


def reset(request, reset_form, profile_model, template, key=None):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)

    msg = None
    if request.method == 'POST':
        form = reset_form(request.POST)
        if form.is_valid():
            # Form class validates email address is registered 
            # to an account.
            try:
                profile = profile_model.objects.get(
                    user__email__exact=form.cleaned_data['email']
                )
            except profile_model.MultipleObjectsReturned:
                # Shouldn't be reached. Added as sanity check. Grab the 
                # first profile that matches this email address.
                profile = profile_model.objects.filter(
                    user__email__exact=form.cleaned_data['email']
                )[0]

            profile.activation_key = profile_model.objects.generate_hash()
            profile.save()

            subject = 'Confirm your password reset request'
            ctext = {
                'key': profile.activation_key,
            }
            profile_model.objects.send_user_email(
                profile.user, 
                subject, 
                ctext, 
                'baseacct/reset_email.txt',
            )

            msg = ('An email has been sent to %s. Please follow the '
                   'instructions in that email to complete your '
                   'password reset.' % profile.user.email)
            return render_to_response(template, {
                'email': profile.user.email,
                'msg': msg,
                'form': form,
                }, context_instance=RequestContext(request))
    else:
        if key is not None:
            user = profile_model.objects.reset_user_password(key)
            if user:
                msg = ('We have reset your password. You will receive an '
                       'email shortly containing your new password. Use '
                       'that to login to your account.')
            else:
                msg = ('Invalid key was given.')
            return render_to_response(template, {
                'msg': msg,
                'form': reset_form(),
                }, context_instance=RequestContext(request))
        else:
            form = reset_form()

    return render_to_response(template, {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def password_change(request, template,
                    password_change_redirect, password_change_form):
    if password_change_redirect is None:
        password_change_redirect = 'baseacct-password-change-done'

    if request.method == 'POST':
        form = password_change_form(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(password_change_redirect)
    else:
        form = password_change_form(request.user)
    
    return render_to_response(template, {
        'form': form,
    }, context_instance=RequestContext(request))