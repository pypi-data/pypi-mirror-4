from nose.plugins import Plugin

class LogbookPlugin(Plugin):  # pragma: no cover
    """logbook compatability"""
    name = 'logbook'
    enabled = True

    def configure(self, options, conf):
        super(LogbookPlugin, self).configure(options, conf)
        self.enabled = True

    def help(self):
        return 'logbook compatability'

    def begin(self):
        from logbook.compat import LoggingHandler
        LoggingHandler().push_application()
