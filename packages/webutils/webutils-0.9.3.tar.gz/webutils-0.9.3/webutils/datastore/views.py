import cPickle
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from webutils.djtools.email import send_simple_email
from webutils.datastore.models import *


def process_form(request, template, formcl, redir, map={}):
    ''' View to store all form data into a text field (pickled)
        map should be a map of form fields to request.GET fields.
        example: {'sale_id': 'oid'}
        This will set the initial value for "formcl" of the 
        field sale_id to whatever oid is set in request.GET
    '''
    if request.method == 'POST':
        form = formcl(request.POST)
        if form.is_valid():
            data = {}
            for key in form.fields.keys():
                data[key] = form.cleaned_data.get(key, '')
            dump = cPickle.dumps(data)
            ds = DataStore.objects.create(dump=dump)
            return HttpResponseRedirect(redir)
    else:
        init = {}
        for key in map.keys():
            init[key] = request.GET.get(map[key], '')
        form = formcl(initial=init)

    return render_to_response(template, {
        'form': form,
        }, context_instance=RequestContext(request))


def process_email_form(request, template, formcl, redir, map={}, defaults={}):
    ''' View to email all form data to an email address.
        Required form field: email_to, email_subject
        all other options are same as process_form above
    '''
    if request.method == 'POST':
        form = formcl(request.POST)
        if form.is_valid():
            data = {}
            for key in form.fields.keys():
                data[key] = form.cleaned_data.get(key, '')
            
            data['ip'] = request.META['REMOTE_ADDR']
            msg = 'The following data was submitted:\n\n'
            msg += '\n'.join(['%s: %s\n' % (k, v) for k, v in data.items()])
            send_simple_email(
                data['email_to'],
                data['email_subject'],
                {},
                msg,
                is_template_file=False,
            )
            return HttpResponseRedirect(redir)
    else:
        init = {}
        for key in map.keys():
            init[key] = request.GET.get(map[key], '')
            init.update(defaults)
        form = formcl(initial=init)

    return render_to_response(template, {
        'form': form,
        }, context_instance=RequestContext(request))
