import os
import tarfile

from testtools import TestCase
from treeshape import FileTree

from ..debuild import (
    _find_binary_files_in_dir,
    build_debian_source_include_binaries_content,
    build_orig_tar_gz,
    )


def DebianTempDirFixture():
    return FileTree(
        {'debian/icons/': {},
         'debian/source/': {}})


class BuildTarTestCase(TestCase):

    def test_build_orig_tar_gz(self):
        tempdir = self.useFixture(DebianTempDirFixture())
        changelog_path = tempdir.join("debian", "changelog")
        with open(changelog_path, "w") as f:
            f.write("""
testpkg (0.1) unstable; urgency=low

  * some changes

 -- Some Guy <foo@example.com>  Thu, 19 Apr 2012 10:53:30 +0200
""")
        with open(tempdir.join("canary"), "w") as f:
            f.write("pieep")
        # build it
        result_path = build_orig_tar_gz(tempdir.path)
        # verify
        self.assertEqual(
            "testpkg_0.1.orig.tar.gz", os.path.basename(result_path))
        with tarfile.open(result_path) as f:
            self.assertEqual(
                ["testpkg-0.1", "testpkg-0.1/canary"],
                [m.name for m in f.getmembers()])


class BuildIncludeBinariesTestCase(TestCase):

    def _make_icons(self, tempdir):
        for icon_name in ["foo.png", "bar.png"]:
            icon_path = tempdir.join('debian', 'icons', icon_name)
            with open(icon_path, "w") as f:
                f.write("x\0x")

    def test_find_binary_files(self):
        tempdir = self.useFixture(DebianTempDirFixture())
        self._make_icons(tempdir)
        bin_files = _find_binary_files_in_dir(tempdir.join('debian'))
        self.assertEqual(
            sorted(["icons/foo.png", "icons/bar.png"]),
            sorted(bin_files))

    def test_build_debian_source_include_binaries_content(self):
        tempdir = self.useFixture(DebianTempDirFixture())
        self._make_icons(tempdir)
        build_debian_source_include_binaries_content(tempdir.path)
        expected_binaries = sorted(
            ['debian/icons/foo.png', 'debian/icons/bar.png'])
        include_binaries = tempdir.join('debian', 'source', "include-binaries")
        with open(include_binaries) as f:
            found_binaries = sorted(line.strip() for line in f.readlines())
        self.assertEqual(expected_binaries, found_binaries)
