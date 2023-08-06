import urllib
import httplib
from filters import Filters
from socket import _GLOBAL_DEFAULT_TIMEOUT as default_timeout
from webutils.helpers import encode_dict
from webutils import __version__ as web_ver


class BaseResponse(object):
    ''' Base HTTP Response Object '''
    def __init__(self, response, data):
        self.response = response
        self.response_data = data
        self.status = response.status
        self.reason = response.reason
        self.headers = dict([k.lower(), v] for k, v in response.getheaders())


class BaseClient(object):
    ''' Very basic REST client.
    '''
    def __init__(self, host, port=None, filters=[],
                 timeout=default_timeout, is_secure=True, debug=False):
        self.host = host
        self.filters = Filters(filters)
        self.timeout = timeout
        self.is_secure = is_secure
        self.debug = debug
        self.headers = {}
        self.request = None
        self.response = None
        if port is not None:
            self.port = port
        else:
            self.port = httplib.HTTPS_PORT if is_secure else httplib.HTTP_PORT

    def send_request(self, method='GET', path='/',
                     request=None, headers={}, opts={}, check_func=None):
        ''' Construct and send request to remote host.
        '''
        self.request = request

        # Apply any filters before request
        self.filters.apply(self)

        if isinstance(self.request, dict):
            self.request = urllib.urlencode(encode_dict(self.request))
        
        if isinstance(headers, dict):
            self.headers.update(headers)

        if opts:
            path += '?%s' % urllib.urlencode(opts)
        
        conn_cls = getattr(
            httplib,
            'HTTPSConnection' if self.is_secure else 'HTTPConnection',
        )
        conn = conn_cls(self.host, self.port, timeout=self.timeout)

        if self.debug:
            print 'DEBUG (method): ', method
            print 'DEBUG (path): ', path
            print 'DEBUG (headers): ', self.headers
            print 'DEBUG (request): ', request

        conn.request(method, path, self.request, self.headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        
        self.response = BaseResponse(res, data)

        if self.debug:
            print 'DEBUG (response data): ', self.response.response_data
            print 'DEBUG (response headers): ', self.response.headers
            print 'DEBUG (response code): %i - %s' % \
                                (self.response.status, self.response.reason)
        
        # Apply any filters after the request
        self.filters.apply(self, 'post_request')
        
        if check_func is not None and callable(check_func):
            return check_func(self)
        return self.response
    
    def get(self, path='/', **kwargs):
        ''' Shortcut for GET request '''
        return self.send_request(method='GET', path=path, **kwargs)
    
    def delete(self, path='/', **kwargs):
        ''' Shortcut for DELETE request '''
        return self.send_request(method='DELETE', path=path, **kwargs)
    
    def post(self, request, path='/', **kwargs):
        ''' Shortcut for POST request '''
        return self.send_request(
            method='POST',
            path=path,
            request=request,
            **kwargs
        )
    
    def update(self, request, path='/', **kwargs):
        ''' Shortcut for UPDATE request '''
        return self.send_request(
            method='UPDATE',
            path=path,
            request=request,
            **kwargs
        )
