"""
Class for accepting PayPal's Instant Payment Notification messages in a 
Django application (or Django-on-App-Engine):

Original snippet found here:

http://www.djangosnippets.org/snippets/969/

I've altered it to fit my own personal needs.
"""
import urllib
from django.http import HttpResponse
from django.utils.encoding import smart_str


class Endpoint(object):
    
    default_response_text = 'Nothing to see here'
    verify_url = "https://www.paypal.com/cgi-bin/webscr"
    
    def do_post(self, url, data):
        return urllib.urlopen(url, data).read()

    def verify(self, request):
        raw_post = getattr(request, 'body', request.raw_post_data)
        raw_post += '&cmd=_notify-validate'
        return self.do_post(self.verify_url, raw_post) == 'VERIFIED'
    
    def default_response(self):
        return HttpResponse(self.default_response_text)
    
    def __call__(self, request):
        r = None
        if request.method == 'POST':
            data = dict(request.POST.items())
            # We need to post that BACK to PayPal to confirm it
            if self.verify(request):
                r = self.process(data)
            else:
                r = self.process_invalid(data)
        if r:
            return r
        else:
            return self.default_response()
    
    def process(self, data):
        pass
    
    def process_invalid(self, data):
        pass
