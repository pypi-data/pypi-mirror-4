from testtools import TestCase

from .. import __version__
from ..backend import (
    EXTERNAL_BACKEND_PATHS,
    StaticBackend,
    )
from ..bin.main import get_version_info
from ..testing import StaticLoaderFixture


class TestVersionInfo(TestCase):

    def test_version_info(self):
        x = get_version_info()
        self.assertEqual("pkgme %s" % (__version__,), x)

    def test_debug_version_info(self):
        backends = [StaticBackend(self.getUniqueString(), 0, {})]
        self.useFixture(StaticLoaderFixture(backends))
        x = get_version_info(debug=True)
        expected_backends = '\n'.join(" %s" % b.describe() for b in backends)
        expected = """pkgme %s

Backend paths: %s
Available backends:
%s""" % (
            __version__,
            ', '.join(map(repr, EXTERNAL_BACKEND_PATHS)),
            expected_backends)
        self.assertEqual(expected, x)
