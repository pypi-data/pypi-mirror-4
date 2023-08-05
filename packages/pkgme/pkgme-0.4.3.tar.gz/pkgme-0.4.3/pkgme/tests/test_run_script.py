import pickle

from testtools import TestCase

from ..run_script import (
    ScriptFailed,
    ScriptUserError,
    )


class TestErrors(TestCase):

    def test_script_failed(self):
        e = ScriptFailed(['foo', 'bar'], 1, ['line 1\n', 'line 2\n'])
        self.assertEqual(
            'foo bar failed with returncode 1. Output:\n'
            ' | line 1\n'
            ' | line 2\n', str(e))

    def test_pickling(self):
        # A ScriptFailed exception can be pickled and then unpickled without
        # loss of data.  This is particularly useful for Celery.
        e = ScriptFailed(['foo', 'bar'], 1, ['line 1\n', 'line 2\n'])
        e1 = pickle.loads(pickle.dumps(e))
        self.assertEqual(str(e), str(e1))

    def test_script_user_error(self):
        e = ScriptUserError(['foo', 'bar'], ['line 1\n', 'line 2\n'])
        self.assertEqual(
            'line 1\n'
            'line 2\n', str(e))
