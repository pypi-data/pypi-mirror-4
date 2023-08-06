import os
import urlparse
from django import template
from django.core.files.storage import get_storage_class
from django.core.files.base import ContentFile
from PIL import Image
from cStringIO import StringIO

register = template.Library()


@register.filter
def thumbnail(file, size='104x104', force_save=False):
    x, y = map(int, size.split('x'))
    try:
        filename = file.path
    except NotImplementedError:
        # Some storages don't support path..
        filename = file.name
    filehead, filetail = os.path.split(filename)
    basename, format = os.path.splitext(filetail)
    miniature = basename + '_' + size + format
    miniature_filename = os.path.join(filehead, miniature)
    filehead, filetail = os.path.split(file.url)
    miniature_url = filehead + '/' + miniature
    storage = get_storage_class()()  # Get storage instance
    if storage.exists(miniature_filename) and not force_save:
        return miniature_url

    image = Image.open(file)
    if image.size[0] < x and image.size[1] < y:
        # New size is bigger than original's size! Don't 
        # create new image.
        miniature_url = file.url
    else:
        stream = StringIO()
        image.thumbnail([x, y], Image.ANTIALIAS)
        image.save(stream, image.format, quality=90)
        storage.save(miniature_filename, ContentFile(stream.getvalue()))

    file.seek(0)  # reset
    return miniature_url
