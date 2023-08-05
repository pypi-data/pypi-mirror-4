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
        log_document = self.doc_type()
        log_document.level = level
        log_document.key = key
        log_document.descr = descr.format(**kwargs)

        for key,item in kwargs.iteritems():
            setattr(log_document, key, item)

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
        for item in qs:
            wrapper.data = item._data
            yield wrapper


log = Logger(LogDocument)

    
