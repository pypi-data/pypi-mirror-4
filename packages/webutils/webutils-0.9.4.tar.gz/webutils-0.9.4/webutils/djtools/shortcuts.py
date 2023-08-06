from django.template import RequestContext
from django.shortcuts import render_to_response

def quick_response(request, template, context={}):
    return render_to_response(
        template,
        context,
        context_instance=RequestContext(request),
    )