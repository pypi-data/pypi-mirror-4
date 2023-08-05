from decimal import Decimal
from datetime import datetime, date
from django.utils.functional import Promise

from ua2.MongoLog.document import LogDocument


class Logger(object):
    INFO = 'INFO'
    ERROR = 'ERROR'
    DEBUG = 'DEBUG'
    NOTICE = 'NOTICE'
    WARNING = 'WARNING'

    def __init__(self, doc_type):
        self.doc_type = doc_type
    
    def log(self, level, key, descr, **kwargs):
        for key, value in kwargs.iteritems():
            if isinstance(value, (Decimal, datetime, date, Promise)):
                kwargs[key] = unicode(value)
            
        log_document = self.doc_type()
        log_document.level = level
        log_document.key = key

        for key,item in kwargs.iteritems():
            setattr(log_document, key, item)

        while True:
            try:
                log_document.descr = descr.format(**kwargs)
                break
            except KeyError, e:
                kwargs[e.args[0]] = '<None>'

        log_document.save(safe=False, validate=False)

    @property
    def objects(self):
        return self.doc_type.objects

    def info(self, *args, **kwargs):
        return self.log(Logger.INFO, *args, **kwargs)

    def error(self, *args, **kwargs):
        return self.log(Logger.ERROR, *args, **kwargs)

    def debug(self, *args, **kwargs):
        return self.log(Logger.DEBUG, *args, **kwargs)

    def notice(self, *args, **kwargs):
        return self.log(Logger.NOTICE, *args, **kwargs)

    def warning(self, *args, **kwargs):
        return self.log(Logger.WARNING, *args, **kwargs)

    def iter_log(self, wrap_cls, qs):
        wrapper = wrap_cls()
        
        for item in qs.ensure_index('stamp'):
            wrapper.data = item._data
            yield wrapper


log = Logger(LogDocument)

    
