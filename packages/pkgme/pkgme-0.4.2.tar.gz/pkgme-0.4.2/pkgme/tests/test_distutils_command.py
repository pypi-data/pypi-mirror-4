from distutils.dist import Distribution
import json
import os

from fixtures import TempDir
from testtools import TestCase

from ..distutils_command.pkgme_info import pkgme_info
from ..testing import PathRequiredTestCase


class pkgme_info_tests(TestCase, PathRequiredTestCase):

    def test_interprets_pkgmeinfo(self):
        dist = Distribution()
        cmd = pkgme_info(dist)
        cmd.initialize_options()
        cmd.pkgmeinfo = "foo,bar"
        cmd.finalize_options()
        self.assertEqual(["foo", "bar"], cmd.pkgmeinfo)

    def test_handles_missing_pkgmeinfo(self):
        dist = Distribution()
        cmd = pkgme_info(dist)
        cmd.initialize_options()
        cmd.finalize_options()
        self.assertEqual([], cmd.pkgmeinfo)

    def test_provides_requested_information(self):
        tempdir = self.useFixture(TempDir()).path
        out_path = os.path.join(tempdir, 'output')
        name = self.getUniqueString()
        dist = Distribution(dict(name=name))
        cmd = pkgme_info(dist)
        cmd.initialize_options()
        cmd.pkgmefile = out_path
        cmd.pkgmeinfo = "package_name"
        cmd.finalize_options()
        cmd.run()
        with open(out_path) as f:
            output = json.loads(f.read())
        self.assertEqual({"package_name": name}, output)

    def test_skips_unknown_info(self):
        tempdir = self.useFixture(TempDir()).path
        out_path = os.path.join(tempdir, "output")
        name = self.getUniqueString()
        dist = Distribution(dict(name=name))
        cmd = pkgme_info(dist)
        cmd.initialize_options()
        cmd.pkgmefile = out_path
        cmd.pkgmeinfo = "nonsense"
        cmd.finalize_options()
        cmd.run()
        with open(out_path) as f:
            output = json.loads(f.read())
        self.assertEqual({}, output)

    def get_cmd_with_metadata(self, metadata):
        dist = Distribution(metadata)
        cmd = pkgme_info(dist)
        cmd.initialize_options()
        cmd.finalize_options()
        return cmd

    def test_package_name(self):
        name = self.getUniqueString()
        cmd = self.get_cmd_with_metadata(dict(name=name))
        self.assertEqual(name, cmd.get_package_name())

    def test_description(self):
        description = self.getUniqueString()
        cmd = self.get_cmd_with_metadata(dict(description=description))
        self.assertEqual(description, cmd.get_description())

    def test_description_with_long_description(self):
        description = self.getUniqueString()
        long_description = "long description"
        cmd = self.get_cmd_with_metadata(
            dict(description=description,
                long_description=long_description))
        self.assertEqual(
            description + "\n " + long_description, cmd.get_description())

    def test_maintainer(self):
        maintainer = self.getUniqueString()
        maintainer_email = self.getUniqueString()
        cmd = self.get_cmd_with_metadata(
            dict(maintainer=maintainer, maintainer_email=maintainer_email))
        self.assertEqual(
            "%s <%s>" % (maintainer, maintainer_email), cmd.get_maintainer())

    def test_maintainer_uses_author(self):
        author = self.getUniqueString()
        author_email = self.getUniqueString()
        cmd = self.get_cmd_with_metadata(
            dict(author=author, author_email=author_email))
        self.assertEqual(
            "%s <%s>" % (author, author_email), cmd.get_maintainer())

    def test_maintainer_uses_unknown(self):
        cmd = self.get_cmd_with_metadata({})
        self.assertEqual("unknown <unknown@unknown>", cmd.get_maintainer())

    def test_architecture_is_all(self):
        cmd = self.get_cmd_with_metadata({})
        self.assertEqual("all", cmd.get_architecture())

    def test_architecture_is_any_with_extensions(self):
        cmd = self.get_cmd_with_metadata({})
        cmd.distribution.ext_modules = [self.getUniqueString()]
        self.assertEqual("any", cmd.get_architecture())

    def test_version(self):
        version = "123"
        cmd = self.get_cmd_with_metadata(dict(version=version))
        self.assertEqual(version, cmd.get_version())

    def test_build_depends_includes_python_all(self):
        cmd = self.get_cmd_with_metadata({})
        self.assertIn("python-all", cmd.get_build_depends())

    def test_build_depends_includes_python_setuptools(self):
        cmd = self.get_cmd_with_metadata({})
        self.assertIn("python-setuptools", cmd.get_build_depends())

    def test_build_depends_examines_install_requires(self):
        # FIXME: we shouldn't really be skipping here, it's a symptom
        # of the fact that there are undocumented dependencies.
        self.skipTestIfPathNotPresent("/usr/share/python/debpython")
        cmd = self.get_cmd_with_metadata({})
        cmd.distribution.install_requires = ["foo"]
        self.assertIn("python-foo", cmd.get_build_depends())

    def test_debhelper_addons_is_python2(self):
        cmd = self.get_cmd_with_metadata({})
        self.assertEqual("python2", cmd.get_debhelper_addons())

    def test_depends_includes_python_depends(self):
        cmd = self.get_cmd_with_metadata({})
        self.assertIn("${python:Depends}", cmd.get_depends())

    def test_depends_includes_misc_depends(self):
        cmd = self.get_cmd_with_metadata({})
        self.assertIn("${misc:Depends}", cmd.get_depends())
