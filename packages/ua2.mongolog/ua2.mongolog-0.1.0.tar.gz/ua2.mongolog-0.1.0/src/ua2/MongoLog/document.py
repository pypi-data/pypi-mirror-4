from datetime import datetime
import mongoengine
import pprint
from django.utils.encoding import force_unicode


class LogDocument(mongoengine.DynamicDocument):
    stamp = mongoengine.DateTimeField(required=True, default=datetime.now)
    descr = mongoengine.StringField()
    key = mongoengine.StringField(max_length=255, required=False)
    level = mongoengine.StringField(max_length=255, required=False)

    meta = {'collection': 'log'}
    

    def __unicode__(self):
        return pprint.pformat(self._data)

    def __str__(self):
        return force_unicode(self).encode('utf-8')

