'''
    Prints thank you page from an aweber redirect.
    Will give the submitted name, email etc. to the template.

    REQUIRES DJANGO
'''
from django.shortcuts import render_to_response
from django.template import RequestContext


def thankyou(request, template, new_data=None):
    # default config, overwrite with new_data
    data = {
        'name': 'name',
        'email': 'from',
    }

    if new_data is not None and isinstance(new_data, dict):
        data.update(new_data)

    return render_to_response(
        template, {
            'name': request.REQUEST.get(data['name'], 'Name'),
            'email': request.REQUEST.get(data['email'], 'Your Email'),
        },
        context_instance=RequestContext(request)
    )
