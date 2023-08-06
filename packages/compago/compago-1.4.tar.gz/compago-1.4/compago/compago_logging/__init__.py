import logging
import logging.handlers
from compago.plugin import Plugin


class LoggingPlugin(Plugin):

    """
    This plugin provides logging within your application's commands. To
    use it, simply add the LoggingPlugin to your application thusly:

        from compago import Application
        from compago_plugins.logging_plugin import LoggingPlugin

        app = Application()
        app.add_plugin(LoggingPlugin())

        @app.command
        def test_command(name):
            app.logging.info('Hello, {0}!'.format(name)

        if __name__ == '__main__':
            app.run()

    You can also provide a few arguments when instantiating LoggingPlugin.

        path - The full path to the log file. By default, this will be
               {appname}.log in your current working directory.
        level - The log level to use. By default, this is logging.INFO.
        format - The log format to use. See the Python logging documentation
                 for formatting info.

    The logger this plugin creates is a rotating file logger. It will
    rotate after the file reaches 10MB in size, keeping a maximum of 5
    old log files.
    """

    def __init__(self, path=None, level=logging.INFO,
                 format='%(asctime)s [%(levelname)s] %(message)s'):
        self.path = path
        self.level = level
        self.format = format

    def after_application_init(self, application):
        application.add_option('--log', dest='do_log', action='store_true', default=False,
                               help='If --log is not specified, logging will not occur.')
        application.add_option('--logfile', dest='logfile',
                               metavar='PATH', dest='logfile', default=application.name,
                               help='Optional path to the logfile. Default: {0}.log'.format(
                                   application.name))
        if not application.do_log:
            return
        self.path = application.logfile
        application.logger = logging.getLogger(application.name)
        root_logger = logging.getLogger()
        application.logger.setLevel(self.level)
        fmtr = logging.Formatter(self.format)
        hdlr = logging.handlers.RotatingFileHandler(self.path,
                                                    maxBytes=10000000,
                                                    backupCount=5)
        hdlr.setFormatter(fmtr)
        hdlr.setLevel(self.level)
        for handler in application.logger.handlers:
            application.logger.removeHandler(handler)
        root_logger.addHandler(hdlr)
        root_logger.info('Logging plugin loaded.')


