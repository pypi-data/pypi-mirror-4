import cPickle
import datetime
from django.conf import settings
from django.db import models


class DataStore(models.Model):
    dump = models.TextField()
    date = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        ordering = ('-date',)

    def __unicode__(self):
        return u'%i' % (self.id)

    def get_store(self):
        return cPickle.loads(self.dump.encode('ascii'))

    def save(self, *args, **kwargs):
        if self.id:
            self.updated = datetime.datetime.now()
        super(DataStore, self).save(*args, **kwargs)
