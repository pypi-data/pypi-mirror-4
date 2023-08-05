from testtools import TestCase
from treeshape import FileTree

from ..backend import ExternalHelpersBackend, get_backend_dir


backend_dir = get_backend_dir(__file__, 'python')


class PythonBackendTests(TestCase):

    def test_want_with_setup_py(self):
        tempdir = self.useFixture(FileTree({'setup.py': {}}))
        backend = ExternalHelpersBackend("python", backend_dir)
        self.assertEqual((20, None), backend.want(tempdir.path))

    def test_want_without_setup_py(self):
        tempdir = self.useFixture(FileTree({}))
        backend = ExternalHelpersBackend("python", backend_dir)
        self.assertEqual(
            (0, "Couldn't find a setup.py"), backend.want(tempdir.path))

    def test_all_info(self):
        tempdir = self.useFixture(
            FileTree({'setup.py': {'content': """\
from distutils.core import setup

setup(name="foo")
"""}}))
        backend = ExternalHelpersBackend("python", backend_dir)
        info = backend.get_info(tempdir.path)
        info = info.get_all(['package_name'])
        self.assertEqual({"package_name": "foo"}, info)
