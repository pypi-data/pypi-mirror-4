import os

from fixtures import TempDir
from testtools import TestCase
from testtools.matchers import (
    DirExists,
    FileContains,
    PathExists,
    )

from ..package_files import PackageFile
from ..write import (
    write_file,
    Writer,
    )


def abspath(fixture, *segments):
    return os.path.join(fixture.path, *segments)


class SimplePackageFile(PackageFile):

    def __init__(self, path, contents="", overwrite=True):
        self.path = path
        self.contents = contents
        self.overwrite = overwrite

    def get_contents(self):
        return self.contents


class WriterTests(TestCase):

    def get_writer(self):
        return Writer()

    def do_write(self, tempdir=None):
        if tempdir is None:
            tempdir = self.useFixture(TempDir())
        writer = self.get_writer()
        writer.write(tempdir.path)
        return tempdir

    def test_write_creates_target_dir(self):
        writer = self.get_writer()
        tempdir = self.useFixture(TempDir())
        target_dir = abspath(tempdir, self.getUniqueString())
        writer.write(
            [SimplePackageFile(self.getUniqueString())], target_dir)
        self.assertThat(target_dir, DirExists())

    def test_write_creates_needed_subdirs(self):
        writer = self.get_writer()
        tempdir = self.useFixture(TempDir())
        subdir = self.getUniqueString()
        package_file = SimplePackageFile(
            os.path.join(subdir, self.getUniqueString()))
        writer.write([package_file], tempdir.path)
        self.assertThat(abspath(tempdir, subdir), DirExists())

    def test_write_accepts_existing_subdir(self):
        writer = self.get_writer()
        tempdir = self.useFixture(TempDir())
        subdir = self.getUniqueString()
        package_file = SimplePackageFile(
            os.path.join(subdir, self.getUniqueString()))
        os.makedirs(abspath(tempdir, subdir))
        writer.write([package_file], tempdir.path)
        self.assertThat(abspath(tempdir, subdir), DirExists())

    def test_write_creates_file(self):
        writer = self.get_writer()
        tempdir = self.useFixture(TempDir())
        filename = self.getUniqueString()
        package_file = SimplePackageFile(filename)
        writer.write([package_file], tempdir.path)
        self.assertThat(abspath(tempdir, filename), PathExists())

    def test_write_creates_file_with_correct_contents(self):
        writer = self.get_writer()
        tempdir = self.useFixture(TempDir())
        filename = self.getUniqueString()
        contents = self.getUniqueString()
        package_file = SimplePackageFile(filename, contents=contents)
        writer.write([package_file], tempdir.path)
        self.assertThat(abspath(tempdir, filename), FileContains(contents))

    def test_write_creates_all_files(self):
        writer = self.get_writer()
        tempdir = self.useFixture(TempDir())
        filename1 = self.getUniqueString()
        package_file1 = SimplePackageFile(filename1)
        filename2 = self.getUniqueString()
        package_file2 = SimplePackageFile(filename2)
        writer.write([package_file1, package_file2], tempdir.path)
        self.assertThat(abspath(tempdir, filename1), PathExists())
        self.assertThat(abspath(tempdir, filename2), PathExists())

    def test_write_overwrites(self):
        writer = self.get_writer()
        tempdir = self.useFixture(TempDir())
        original_contents = self.getUniqueString()
        new_contents = self.getUniqueString()
        filename = self.getUniqueString()
        target_path = abspath(tempdir, filename)
        write_file(target_path, original_contents)
        package_file = SimplePackageFile(
            filename, contents=new_contents, overwrite=True)
        writer.write([package_file], tempdir.path)
        self.assertThat(target_path, FileContains(new_contents))

    def test_write_doesnt_overwrite_files_with_overwrite_False(self):
        writer = self.get_writer()
        tempdir = self.useFixture(TempDir())
        original_contents = self.getUniqueString()
        new_contents = self.getUniqueString()
        filename = self.getUniqueString()
        target_path = abspath(tempdir, filename)
        write_file(target_path, original_contents)
        package_file = SimplePackageFile(
            filename, contents=new_contents, overwrite=False)
        writer.write([package_file], tempdir.path)
        self.assertThat(target_path, FileContains(original_contents))

    def test_write_encodes_unicode(self):
        writer = self.get_writer()
        tempdir = self.useFixture(TempDir())
        contents = u"\x80"
        filename = self.getUniqueString()
        target_path = abspath(tempdir, filename)
        package_file = SimplePackageFile(filename, contents=contents)
        writer.write([package_file], tempdir.path)
        self.assertThat(target_path, FileContains(contents.encode('utf-8')))
