import os
import tarfile

from testtools import TestCase
from treeshape import FileTree

from ..debuild import (
    _find_binary_files_in_dir,
    build_debian_source_include_binaries_content,
    build_orig_tar_gz,
    )


def expand_path_components(path):
    """Get all the path components that are needed to mkdir `path`.

        get_all_paths('foo') == ['foo']
        get_all_paths('foo/bar') == ['foo', 'foo/bar']
        get_all_paths('foo/bar/baz') == ['foo', 'foo/bar', 'foo/bar/baz']
        get_all_paths('') == []
    """
    parts = []
    while path != '':
        parts.insert(0, path)
        path = os.path.dirname(path)
    return parts


def DebianTempDirFixture():
    return FileTree(
        {'debian/icons/': {},
         'debian/source/': {}})


class BuildTarTestCase(TestCase):

    def make_debian_tempdir(self):
        tempdir = self.useFixture(DebianTempDirFixture())
        changelog_path = tempdir.join("debian", "changelog")
        with open(changelog_path, "w") as f:
            f.write("""
testpkg (0.1) unstable; urgency=low

  * some changes

 -- Some Guy <foo@example.com>  Thu, 19 Apr 2012 10:53:30 +0200
""")
        return tempdir

    def test_build_orig_tar_gz(self):
        tempdir = self.make_debian_tempdir()
        with open(tempdir.join("canary"), "w") as f:
            f.write("peep")
        # build it
        result_path = build_orig_tar_gz(tempdir.path)
        # verify
        self.assertEqual(
            "testpkg_0.1.orig.tar.gz", os.path.basename(result_path))
        with tarfile.open(result_path) as f:
            self.assertEqual(
                ["testpkg-0.1", "testpkg-0.1/canary"],
                [m.name for m in f.getmembers()])

    def test_build_orig_tar_gz_not_exclude_other_debian(self):
        tempdir = self.make_debian_tempdir()
        canary_filename = "something/debian/canary"
        os.makedirs(tempdir.join(os.path.dirname(canary_filename)))
        with open(tempdir.join(canary_filename), "w") as f:
            f.write("pieep")
        result_path = build_orig_tar_gz(tempdir.path)
        canary_paths = expand_path_components(canary_filename)
        expected_paths = ["testpkg-0.1"]
        expected_paths += ["testpkg-0.1/" + path for path in canary_paths]
        with tarfile.open(result_path) as f:
            self.assertEqual(expected_paths,
                [m.name for m in f.getmembers()])

    def test_build_orig_tar_gz_preserves_absolute_symlinks(self):
        tempdir = self.make_debian_tempdir()
        source = 'source'
        target = '/a/path'
        os.symlink(target, tempdir.join(source))
        result_path = build_orig_tar_gz(tempdir.path)
        with tarfile.open(result_path) as f:
            info = f.getmember("testpkg-0.1/" + source)
            self.assertEqual(target, info.linkname)


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
