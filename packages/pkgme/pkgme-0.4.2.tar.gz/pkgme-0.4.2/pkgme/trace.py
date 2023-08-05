import logging
import os

from fixtures import Fixture

from pkgme.write import touch


def get_log_location():
    """Return the path that we're logging to."""
    log_dir = os.environ.get("PKGME_LOG_DIR", None)
    log_filename = 'pkgme.log'
    if log_dir is None:
        log_dir = os.path.expanduser(os.path.join('~', '.cache', 'pkgme'))
    return os.path.join(log_dir, log_filename)


class LoggingFixture(Fixture):

    def __init__(self, name, filename, level):
        super(LoggingFixture, self).__init__()
        self._name = name
        self._filename = filename
        self._level = level
        self._logger = logging.getLogger(self._name)

    def _make_handler(self):
        # Make sure that the log file exists.
        touch(self._filename)
        handler = logging.FileHandler(self._filename)
        handler.setLevel(self._level)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        return handler

    def setUp(self):
        super(LoggingFixture, self).setUp()
        handler = self._make_handler()
        loggers = [self._logger, logging.getLogger('debpython')]
        for logger in loggers:
            self.addCleanup(
                setattr, logger, 'handlers', list(logger.handlers))
            self.addCleanup(logger.setLevel, logger.level)
            logger.handlers = []
            logger.addHandler(handler)
            logger.setLevel(self._level)
        return self._logger

    @classmethod
    def get_default(cls, level=logging.INFO):
        return cls('pkgme', get_log_location(), level)


_logger = logging.getLogger('pkgme')

_logging_fixture = LoggingFixture.get_default()
_logging_fixture.setUp()


def debug(message):
    _logger.debug(message)

def log(message):
    _logger.info(message)


def set_debug():
    _logger.setLevel(logging.DEBUG)
    for handler in _logger.handlers:
        handler.setLevel(logging.DEBUG)
