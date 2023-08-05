import os

from fixtures import (
    EnvironmentVariableFixture,
    TempDir,
    TempHomeDir,
    )
from testtools import TestCase
from testtools.matchers import MatchesRegex

from .. import trace


_date_time_re = r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d'

class TestLogging(TestCase):

    def with_temp_home(self):
        return self.useFixture(TempHomeDir())

    def with_temp_log(self):
        self.with_temp_home()
        self.useFixture(trace.LoggingFixture.get_default())

    def test_log_location(self):
        # We log to the XDG cache home.
        temp_home = self.with_temp_home()
        log_location = trace.get_log_location()
        self.assertEqual(
            os.path.join(temp_home.path, '.cache', 'pkgme', 'pkgme.log'),
            log_location)

    def test_log_location_from_env_var(self):
        # If PKGME_LOG_DIR is set in the environment we log there.
        self.with_temp_home()
        temp_dir = self.useFixture(TempDir())
        self.useFixture(EnvironmentVariableFixture('PKGME_LOG_DIR', temp_dir.path))
        log_location = trace.get_log_location()
        self.assertEqual(os.path.join(temp_dir.path, 'pkgme.log'), log_location)

    def test_log_to_file(self):
        self.with_temp_log()
        trace.log("message")
        log_location = trace.get_log_location()
        with open(log_location) as f:
            log_contents = f.read()
        self.assertThat(
            log_contents,
            MatchesRegex(r'%s - INFO - message\n' % (_date_time_re,)))

    def test_log_twice(self):
        self.with_temp_log()
        trace.log("first")
        trace.log("second")
        log_location = trace.get_log_location()
        with open(log_location) as f:
            log_contents = f.read()
        self.assertThat(
            log_contents,
            MatchesRegex(
                r'%s - INFO - first\n%s - INFO - second\n' % (
                    _date_time_re, _date_time_re)))

    def test_log_appends(self):
        self.with_temp_log()
        trace.log("first")
        trace.LoggingFixture.get_default()
        trace.log("second")
        log_location = trace.get_log_location()
        with open(log_location) as f:
            log_contents = f.read()
        self.assertThat(
            log_contents,
            MatchesRegex(
                r'%s - INFO - first\n%s - INFO - second\n' % (
                    _date_time_re, _date_time_re)))

    def test_set_debug(self):
        self.with_temp_log()
        trace.set_debug()
        trace.debug("Hello")
        with open(trace.get_log_location()) as f:
            log_contents = f.read()
        self.assertThat(
            log_contents,
            MatchesRegex(
                r'%s - DEBUG - Hello\n' % (_date_time_re,)))
