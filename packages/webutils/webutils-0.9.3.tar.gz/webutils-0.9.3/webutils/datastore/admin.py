from django.contrib import admin
from webutils.datastore.models import *


class DataStoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'date')
    ordering = ('-date',)
admin.site.register(DataStore, DataStoreAdmin)
