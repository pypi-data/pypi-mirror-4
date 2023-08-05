import json
import os
import pkg_resources
from StringIO import StringIO

from fixtures import (
    EnvironmentVariableFixture,
    MonkeyPatch,
    )
from testtools import TestCase
from testtools.matchers import (
    DirContains,
    DirExists,
    Not,
    )
from treeshape import FileTree

from ..api import (
    get_all_info,
    load_backends,
    packaging_info_as_data,
    )


class ScriptTests(TestCase):
    """Smoke tests for the top-level pkgme script."""

    def setUp(self):
        super(ScriptTests, self).setUp()
        # The DEBEMAIL environment variable is consulted when the
        # pacakging is written, so set it to a known value for proper
        # isolation
        debemail = 'Dude <dude@example.com>'
        self.useFixture(EnvironmentVariableFixture('DEBEMAIL', debemail))

    def run_script(self, cwd, argv=None):
        if argv is None:
            argv = []
        ep = pkg_resources.load_entry_point(
            "pkgme", "console_scripts", "pkgme")
        stderr = StringIO()
        stdout = StringIO()
        with MonkeyPatch('sys.stdout', stdout):
            with MonkeyPatch('sys.stderr', stderr):
                try:
                    ep(argv=argv, target_dir=cwd, interactive=False)
                except SystemExit:
                    # If the script exits due to a failure, we don't want to exit
                    # the whole test suite.
                    pass
        self.assertEqual('', stderr.getvalue())
        return stdout.getvalue()

    def create_marker_file(self, prefix=None):
        """Create the file that triggers the dummy backend for testing."""
        path = "is_pkgme_test"
        if prefix is not None:
            path = os.path.join(prefix, path)
        return self.useFixture(FileTree({path: {}}))

    def test_writes_files(self):
        tempdir = self.create_marker_file()
        self.run_script(tempdir.path)
        self.assertThat(tempdir.join("debian"), DirExists())

    def test_builds_source_package(self):
        tempdir = self.create_marker_file(prefix="foo")
        self.run_script(tempdir.join('foo'))
        self.assertThat(tempdir.path, DirContains(
            ["foo_0.0.0.orig.tar.gz",
             "foo_0.0.0.debian.tar.gz",
             "foo_0.0.0.dsc",
             "foo_0.0.0_source.build",
             "foo_0.0.0_source.changes",
             "foo",
             ]))

    def test_nobuild_doesnt_builds_source_package(self):
        tempdir = self.create_marker_file(prefix="foo")
        self.run_script(tempdir.join('foo'), ['--nobuild'])
        self.assertThat(tempdir.path, DirContains(["foo"]))

    def test_which_backends(self):
        tempdir = self.create_marker_file()
        output = self.run_script(tempdir.path, ['--which-backends'])
        self.assertEqual('dummy (100)\n', output)
        self.assertThat(tempdir.join("debian"), Not(DirExists()))

    def test_dump(self):
        tempdir = self.create_marker_file()
        all_info = get_all_info(tempdir.path, load_backends())
        clean_info = packaging_info_as_data(all_info)
        output = self.run_script(tempdir.path, ['--dump'])
        self.assertEqual(clean_info, json.loads(output))
        self.assertThat(tempdir.join("debian"), Not(DirExists()))

    def test_nosign(self):
        tempdir = self.create_marker_file(prefix='foo')
        self.run_script(tempdir.join('foo'), ['--nosign'])
        changes_file = os.path.join(tempdir.path,
                                    "foo_0.0.0_source.changes")
        signature = open(changes_file)
        sig_text = signature.readlines()
        signature.close()
        self.assertNotIn(sig_text, "-----BEGIN PGP SIGNATURE-----\n")
