from logging import Handler, NOTSET, Filterer, _acquireLock, _releaseLock

# Reverse definition of levels
levels = {50: "CRITICAL", 40: "ERROR", 30: "WARNING",
          20: "INFO", 10: "DEBUG", 0: "NOTSET"}


class SimplemailLogger(Handler):
    def __init__(self, mailobject, app=None, level=NOTSET):
        """ SimpleLogger constructor
        Just duplicate standard Handler and add:
        - self.mailobject for simplemail instance.
        - self.app for your application name.
        """
        Filterer.__init__(self)
        self._name = None
        self.level = level
        self.formatter = None
        _acquireLock()
        self.createLock()
        self.mailobject = mailobject
        if app:
            self.app = app
        else:
            self.app = None
        _releaseLock()

    def emit(self, record):
        """ emit method
        Send email using passed simplemail instance (self.mailobject) if
        record.levelno >= self.level.  Prefix the subject with application
        name if self.app was defined in constructor.
        """
        if record.levelno >= self.level:
            if self.app:
                subj = "[%s] %s error occured" % (self.app,
                                                    levels[record.levelno])
            else:
                subj = "%s error occured" % levels[record.levelno]
            self.mailobject.send(subject=subj, body=record.msg)
