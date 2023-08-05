"""Configure logging subsystem."""
from __future__ import absolute_import

from logging.handlers import WatchedFileHandler
import logging
import sys

from thriftpool.signals import setup_logging, after_logging_setup
from thriftpool.utils.logs import ColorFormatter, LoggingProxy
from thriftpool.utils.term import colored, isatty
from thriftpool.utils.debug import RequestLogger

__all__ = ['Logging']


class Logging(object):
    """Setup logging subsystem."""

    app = None

    def __init__(self):
        self.logfile = self.app.config.LOG_FILE
        self.loglevel = self.app.config.LOGGING_LEVEL
        self.format = self.app.config.DEFAULT_LOG_FMT
        self.colored = colored(enabled=self.colorize(self.logfile))
        self.request_logger = None

    def redirect_stdouts_to_logger(self, logger, loglevel=None,
                                   stdout=True, stderr=True):
        """Redirect :class:`sys.stdout` and :class:`sys.stderr` to a
        logging instance.

        :param logger: The :class:`logging.Logger` instance to redirect to.
        :param loglevel: The loglevel redirected messages will be logged as.

        """
        proxy = LoggingProxy(logger, loglevel)
        if stdout:
            sys.stdout = proxy
        if stderr:
            sys.stderr = proxy
        return proxy

    def get_handler(self, logfile=None):
        """Create log handler with either a filename, an open stream
        or :const:`None` (stderr).

        """
        logfile = sys.stderr if logfile is None else logfile
        if hasattr(logfile, 'write'):
            return logging.StreamHandler(logfile)
        return WatchedFileHandler(logfile)

    def colorize(self, logfile=None):
        """Can be output colored?"""
        return isatty(sys.stderr) if logfile is None else False

    def setup_handlers(self, logger, logfile, format, formatter=ColorFormatter):
        """Register needed handlers for given logger. If ``logfile`` equal to 
        :const:`None` use :attr:`sys.stderr` as ``logfile``.

        """
        colorize = self.colorize(logfile)
        datefmt = '%H:%M:%S' if logfile is None else '%Y-%m-%d %H:%M:%S'
        handler = self.get_handler(logfile)
        handler.setFormatter(formatter(format, use_color=colorize, datefmt=datefmt))
        logger.addHandler(handler)
        return logger

    def setup_request_logging(self):
        """Setup system to log requests."""
        logger = logging.getLogger('thriftpool.requests')
        self.request_logger = RequestLogger(logger, self.colored)
        self.request_logger.setup()

    def setup(self):
        root = logging.getLogger()
        root.setLevel(self.loglevel)
        receivers = setup_logging.send(sender=self, root=root,
                                       logfile=self.logfile,
                                       loglevel=self.loglevel)
        if not receivers:
            self.setup_handlers(root, self.logfile, self.format)
            after_logging_setup.send(sender=self, root=root,
                                    logfile=self.logfile,
                                    loglevel=self.loglevel)
        logger = logging.getLogger('thriftpool.stdout')
        self.redirect_stdouts_to_logger(logger)
        if self.app.config.LOG_REQUESTS:
            self.setup_request_logging()
