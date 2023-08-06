from django.conf import settings
from django.db import models


class IsActiveManager(models.Manager):
    def __init__(self, field_name='is_active', 
                 field_value=True, *args, **kwargs):
        self.field_name = field_name
        self.field_value = field_value
        super(IsActiveManager, self).__init__(*args, **kwargs)

    def get_query_set(self):
        qs = super(IsActiveManager, self).get_query_set()
        return qs.filter(**{self.field_name: self.field_value})
