import base64
from webutils.xmlparser import Parser


class Filters(object):
    ''' Base Client Filter Class
        Idea taken from restkit. (http://github.com/benoitc/restkit)
        
        This is a much simpler, and less featureful, system.
    '''
    def __init__(self, filters=[]):
        if filters:
            if isinstance(filters, tuple):
                filters = list(filters)
            if not isinstance(filters, list):
                filters = [filters]
        self.filters = filters or []
        
        # Validate filters
        self.check_filters()
    
    def check_filters(self, filters=None):
        ck_filters = filters or self.filters
        for f in ck_filters:
            if not hasattr(f, 'pre_request') and \
               not hasattr(f, 'post_request'):
                raise TypeError(
                    '%s is not a filter object.' % f.__class__.__name__
                )
    
    def add(self, obj):
        self.check_filters([obj])
        self.filters.append(obj)

    def remove(self, obj):
        for i, f in enumerate(self.filters):
            if obj == f:
                del self.filters[i]

    def apply(self, obj, method='pre_request'):
        for f in self.filters:
            try:
                func = getattr(f, method)
                func(obj)
            except AttributeError:
                continue


class BasicAuthFilter(object):
    ''' Basic Auth Filter '''
    def __init__(self, username, password):
        self.credentials = (username, password)

    def pre_request(self, client):
        encode = base64.b64encode('%s:%s' % self.credentials)
        client.headers.update({'Authorization': 'Basic %s' %  encode})


class XMLParserFilter(object):
    ''' Filter to parse in/out data to/from XML.
    
        Depends on the webutils.xmlparser.Parser class
    '''
    parser = Parser()
    
    def pre_request(self, client):
        if client.request is not None:
            client.request = self.parser.build_request_string(client.request)
    
    def post_request(self, client):
        rdata = client.response.response_data
        client.response.parsed_data = \
                    self.parser.parse(rdata) if rdata else None
