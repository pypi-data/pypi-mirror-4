import gc
from django.conf import settings
from django.template.defaultfilters import slugify
from webutils.helpers import grab_from_import


def import_setting_name(setting_name, default_obj=None):
    ''' Used to import an item from a value in the current 
        Django projects settings.py
        
        Example in settings.py:
        
            FORM_TO_IMPORT = 'myproject.myapp.forms.CustomForm'
        
        Then to grab this, just call import_setting_name:
        
            form = import_setting_name('FORM_TO_IMPORT')
        
        Pass 'default_obj' 
    '''
    if hasattr(settings, setting_name):
        try:
            return grab_from_import(
                getattr(settings, setting_name),
                as_from=True,
            )
        except ImportError, err:
            if default_obj is None:
                raise ImportError(str(err))
    return default_obj


def slugify_uniquely(s, queryset=None, field='slug'):
    '''
    --> Taken from django-crm models.py

    Returns a slug based on 's' that is unique for all instances of the given
    field in the given queryset.
    
    If no string is given or the given string contains no slugify-able
    characters, default to the given field name + N where N is the number of
    default slugs already in the database.
    '''
    new_slug = new_slug_base = slugify(s)
    if queryset is not None:
        queryset = queryset.filter(**{'%s__startswith' % field: new_slug_base})
        similar_slugs = [value[0] for value in queryset.values_list(field)]
        i = 1
        while new_slug in similar_slugs:
            new_slug = "%s%d" % (new_slug_base, i)
            i += 1
    return new_slug


# Taken from http://djangosnippets.org/snippets/1949/
def queryset_iterator(queryset, chunksize=1000):
    ''' Iterate over a Django Queryset ordered by the primary key

        This method loads a maximum of chunksize (default: 1000) rows in it's
        memory at the same time while django normally would load all rows in it's
        memory. Using the iterator() method only causes it to not preload all the
        classes.

        Note that the implementation of the iterator does not support ordered query sets.
        
        Example Usage:

        my_queryset = queryset_iterator(MyModel.objects.all())
        for row in my_queryset:
            print row.pk
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()
