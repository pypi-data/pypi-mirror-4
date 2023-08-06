'''
    Requires django!
    Provide cache functions for django views, etc.
'''
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpRequest
from django.template import Context, loader
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.cache import get_cache_key
from django.core.cache.backends.memcached import CacheClass as DjCacheClass


def basic_cached_response(template_file, ctext=None, *args, **kwargs):
    cache_name = '%s_%s' % (settings.ROOT_URLCONF, template_file)
    ctext = ctext or {}
    tmpl = cache.get(cache_name)
    if tmpl is None:
        tmpl = loader.get_template(template_file)
        cache.set(cache_name, tmpl)

    mimetype = {'mimetype': kwargs.pop('mimetype', None)}
    context = kwargs.pop('context_instance', None)
    if context is not None:
        context.update(ctext)
    else:
        context = Context(ctext)

    return HttpResponse(tmpl.render(context), **mimetype)


def expire_view_cache(view_name, args=[], namespace=None, key_prefix=None):
    """
    This function allows you to invalidate any view-level cache. 
        view_name: view function you wish to invalidate or it's 
                   named url pattern
        args: any arguments passed to the view function
        namepace: optioal, if an application namespace is needed
        key prefix: for the @cache_page decorator for the function (if any)
        
        http://stackoverflow.com/questions/2268417/expire-a-view-cache-in-django
    """
    # create a fake request object
    request = HttpRequest()
    
    # Loookup the request path:
    if namespace:
        view_name = namespace + ":" + view_name

    try:
        request.path = reverse(view_name, args=args)
    except NoReverseMatch:
        return False

    # get cache key, expire if the cached item exists:
    key = get_cache_key(request, key_prefix=key_prefix)
    if key:
        if cache.get(key):
            cache.set(key, None, 0)
        return True
    return False


class CacheClass(object):
    ''' Cache class that uses the Django memcached CacheClass
        but adds support for key prefix's. Should be done in 
        the django level, but this is a work around for now.
    '''
    def __init__(self, server, params):
        self._cache = DjCacheClass(server, params)
        self.prefix = getattr(settings, 'CACHE_PREFIX', '')

    def add_prefix(self, key):
        if self.prefix:
            return '%s-%s' % (self.prefix, key)
        return key

    def add(self, key, value, timeout=0):
        key = self.add_prefix(key)
        return self._cache.add(key, value, timeout)

    def get(self, key, default=None):
        key = self.add_prefix(key)
        return self._cache.get(key, default)

    def set(self, key, value, timeout=0):
        key = self.add_prefix(key)
        return self._cache.set(key, value, timeout)

    def delete(self, key):
        key = self.add_prefix(key)
        return self._cache.delete(key)

    def get_many(self, keys):
        keys = map(self.add_prefix, keys)
        return self._cache.get_many(keys)

    def close(self, **kwargs):
        self._cache.close(**kwargs)

    def incr(self, key, delta=1):
        key = self.add_prefix(key)
        return self._cache.incr(key, delta)

    def decr(self, key, delta=1):
        key = self.add_prefix(key)
        return self._cache.decr(key, delta)
