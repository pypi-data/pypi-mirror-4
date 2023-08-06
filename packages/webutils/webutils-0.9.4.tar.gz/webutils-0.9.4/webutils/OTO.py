'''
    Class to offer a "One Time Only" Offer for your 
    sales pages.

    This will allow you to offer pages on a "one time only" 
    basis. It will track the current position based on a 
    cookie that is named after your project name (taken 
    from settings.ROOT_URLCONF).

    Initiate the instance with a tuple, or list, of OTO templates. 
    In other words, how many "one time offers" you want to go 
    through before finally settling on the "final_template".

    It also accepts a variable named "cookie_days" which is a setting 
    for how many days the cookie should live on the users browser.

    Example usage in urls.py..

    from yourproject.OTO import OTO

    oto_templates = ('template1.html', 'template2.html', 'template3.html')
    urlpatterns = patterns('',
        (r'^oto/$',
            OTO(oto_templates, 'final_template.html')),
    )

    Head to yourdomain.com/oto you will see template1.html rendered. Reload 
    for template2.html, template3.html and eventually final_template.html

    You can set settings.OTO_COOKIE_DOMAIN to manually set the domain 
    that the cookie is set for. Otherwise it checks the Site framework and 
    if that fails, uses request.get_host() (requires Django 1.0+!)

    Peter Sanchez
    pjs@petersanchez.com - www.petersanchez.com
'''
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.sites.models import Site


class OTO(object):
    def __init__(self, oto_templates, final_template, cookie_days=180):
        if not isinstance(oto_templates, (list, tuple)):
            oto_templates = (oto_templates,)

        self.oto_templates = oto_templates
        self.final_template = final_template
        self.cookie_days = cookie_days

        self.cookie_str = '%s-oto' % (settings.ROOT_URLCONF.split('.')[0])
        self.cookie_domain = None

    def _getvars(self, request):
        getvars = request.GET.copy()
        if len(getvars.keys()) > 0:
            return '&%s' % getvars.urlencode()
        return ''

    def return_response(self, request, template):
        return render_to_response(template, {
            'cookie_domain': self.cookie_domain,
            'getvars': self._getvars(request),
            }, context_instance=RequestContext(request))

    def get_cookie_domain(self, request):
        if hasattr(settings, 'OTO_COOKIE_DOMAIN'):
            self.cookie_domain = settings.OTO_COOKIE_DOMAIN
        else:
            try:
                site = Site.objects.get_current()
                self.cookie_domain = site.domain
            except Site.DoesNotExist:
                self.cookie_domain = request.get_host()

    def __call__(self, request):
        oto_count = 0
        if self.cookie_domain is None:
            self.get_cookie_domain(request)

        if self.cookie_str in request.COOKIES:
            try:
                oto_count = int(request.COOKIES[self.cookie_str])
            except ValueError:
                pass

        if oto_count > (len(self.oto_templates) - 1):
            # Been through all the OTO's, send the final template
            return self.return_response(request, self.final_template)
        
        response = self.return_response(request, self.oto_templates[oto_count])
        response.set_cookie(
            self.cookie_str,
            value=(oto_count + 1),
            domain=self.cookie_domain,
            max_age=(((60 * 60) * 24) * self.cookie_days)
        )
        return response
