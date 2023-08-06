'''
    *** DO NOT USE ***
    This was the original "APIClient" I hacked together 
    quickly one day for quick use and testing for an 
    internal project. Over time various apps became 
    dependent on it, which is the only reason it's still 
    here. Yes, I'm embarrassed.
    
    Once I update those apps (one day) to use the new 
    BaseClient + Filters I will remove this from the 
    code repo.
    
    *** DO NOT USE ***
'''
import urllib
import urllib2
import hashlib
import urlparse
from webutils.helpers import encode_dict


class APIError(Exception):
    ''' General exception
    '''
    pass


class APIClient(object):
    def __init__(self, url, key, debug=False):
        url_scheme = urlparse.urlparse(url)
        self.url = url
        self.key = key
        self.scheme = url_scheme.scheme
        self.host = url_scheme.netloc
        self.port = url_scheme.port or 80
        self.path = url_scheme.path
        self.debug = debug

    def create_hash(self, command):
        return hashlib.sha1(self.key + command).hexdigest()

    def send_data(self, params, use_hash=False):
        assert isinstance(params, dict)
        if use_hash and 'command' in params:
            params.update({
                'hash': self.create_hash(params['command']),
            })
        
        return self.send_request(params)

    def send_request(self, request):
        params = urllib.urlencode(encode_dict(request))
        if self.debug:
            print 'DEBUG: ', params

        try:
            uop = urllib2.urlopen(self.url, params)
            code = uop.getcode()
            data = uop.read()
            uop.close()
        except urllib2.HTTPError, err:
            raise APIError(err)

        if code != 200:
            hash = {'statusmsg': '%i - %s' % (code, uop.msg)}
            return False, hash

        if data[:2] != 'OK':
            hash = {
                'statusmsg': data,
            }
            return False, hash

        return True, data