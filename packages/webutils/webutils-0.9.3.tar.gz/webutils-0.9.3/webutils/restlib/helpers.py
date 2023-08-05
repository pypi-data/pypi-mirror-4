import urlparse
from restlib import BaseClient
from socket import _GLOBAL_DEFAULT_TIMEOUT as default_timeout


def url_to_base_client(url, filters=[], timeout=default_timeout, debug=False):
    ''' Takes a full URL and returns a dict with appropriate 
        data, including a "ready" BaseClient instance.
    '''
    url_scheme = urlparse.urlparse(url)
    host = url_scheme.netloc
    port = url_scheme.port
    is_secure = (url_scheme.scheme == 'https')
    bc = BaseClient(
        host,
        port,
        filters=filters,
        timeout=timeout,
        is_secure=is_secure,
        debug=debug,
    )
    res = {}
    for field in url_scheme._fields:
        res[field] = getattr(url_scheme, field)
        if field == 'path' and res[field] == '':
            res[field] = '/'
    bc.url_data = res
    return bc