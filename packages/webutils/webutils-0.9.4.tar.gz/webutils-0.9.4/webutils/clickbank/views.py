'''
    ClickBank Views
    
    REQUIRES DJANGO
'''
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from webutils.clickbank.hashproc import thankyou_check


def index(request, template, cb_template):
    '''
        If refer is from Clickbank, print given template.
        If it's not from CB, print other given template.

        Checks for 'hop' in request.GET.
    '''
    affiliate = None
    if 'hop' in request.GET:
        affiliate = request.GET['hop']
    elif 'cb_affiliate' in request.COOKIES:
        affiliate = request.COOKIES['cb_affiliate']

    response = render_to_response(cb_template if affiliate else template, {
                                  'affiliate': affiliate,
                                  }, context_instance=RequestContext(request))

    if affiliate is not None and 'cb_affiliate' not in request.COOKIES:
        # set cookie so if the user returns, the affiliate
        # gets credit.
        response.set_cookie(
            'cb_affiliate',
            value=affiliate,
            max_age=(((60 * 60) * 24) * 62)  # 62 days
        )
    return response


def thankyou(request, template):
    '''
        Used to verify the authenticity of the CB thank you page 
        request.
        *REQUIRES* CB_KEY be set to your clickbank secret key 
        in settings...
    '''
    if not thankyou_check(settings.CB_KEY, request.GET):
        return HttpResponse('ACCESS DENIED')

    return render_to_response(template, {
            'cname': request.GET['cname'].split(' ')[0],
            'cemail': request.GET['cemail'],
        }, context_instance=RequestContext(request))
