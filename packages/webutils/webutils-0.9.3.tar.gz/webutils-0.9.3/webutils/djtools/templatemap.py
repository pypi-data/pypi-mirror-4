'''
Used to create maps of template variables in the following format:

{variable}

Into Django readable template variables ({{ variable }})
'''

from django.template import loader, Context
from django.http import HttpResponse


def get_template_source(template_name):
    ''' Return a string and origin for template
    '''
    return loader.find_template_source(template_name)


def load_map(source, vmap={}):
    ''' Create map replacements in given source.
    '''
    for key, value in vmap.items():
        key_str = '{%s}' % key
        val_str = '{{ %s }}' % value
        source = source.replace(key_str, val_str)
    return source


def get_mapped_template(template_name, vmap={}):
    ''' Return a mapped template object
        map should be a dict in the following format:
        
        {'variable': 'django_template_variable',}
        
        This will turn all instances of {variable} in the 
        template source into {{ django_template_variable }}
    '''
    source, origin = get_template_source(template_name)
    source = load_map(source, vmap)
    return loader.get_template_from_string(source, origin, template_name)


def get_mapped_template_from_string(source, vmap={}):
    ''' Return template object from incoming source
    '''
    source = load_map(source, vmap)
    return loader.get_template_from_string(source)


def render_to_mapped_string_from_string(source, dictionary=None, vmap=None):
    ''' Shortcut for string response.
    '''
    dictionary = dictionary or {}
    vmap = vmap or {}
    t = get_mapped_template_from_string(source, vmap)
    return t.render(Context(dictionary))


def render_to_mapped_string(template_name, dictionary=None, 
                                    context_instance=None, vmap=None):
    ''' Shortcut for response usage.
    '''
    dictionary = dictionary or {}
    vmap = vmap or {}
    t = get_mapped_template(template_name, vmap)
    if context_instance:
        context_instance.update(dictionary)
    else:
        context_instance = Context(dictionary)
    return t.render(context_instance)


def render_to_mapped_response(*args, **kwargs):
    ''' Shortcut to create mapped HttpResponse object.
    '''
    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    return HttpResponse(
        render_to_mapped_string(*args, **kwargs),
        **httpresponse_kwargs
    )