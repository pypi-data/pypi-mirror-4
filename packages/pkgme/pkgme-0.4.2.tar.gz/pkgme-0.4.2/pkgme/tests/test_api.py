import os

from fixtures import TempDir
from testtools import TestCase
from treeshape import HasFileTree

from .. import write_packaging
from ..api import write_packaging_info
from ..backend import StaticBackend
from ..info_elements import (
    Architecture,
    Description,
    Maintainer,
    PackageName,
    Version,
    )
from ..package_files import Control, DEBIAN_DIR
from ..project_info import DictInfo
from ..testing import (
    ControlSourceStanzaHasField,
    StaticLoaderFixture,
    )


def ControlHasSourceName(name):
    control_path = os.path.join(DEBIAN_DIR, Control.filename)
    return HasFileTree(
        {control_path:
             {'content': ControlSourceStanzaHasField("Source", name)}})


class WritePackagingTests(TestCase):

    def make_info(self, name):
        info = DictInfo(
            {
                PackageName.name: name,
                Maintainer.name: self.getUniqueString(),
                Architecture.name: "all",
                Description.name: self.getUniqueString(),
                Version.name: "1",
            })
        return info

    def test_write_packaging(self):
        name = PackageName.clean(self.getUniqueString())
        info = self.make_info(name)
        tempdir = self.useFixture(TempDir()).path
        backend = StaticBackend(
            self.getUniqueString(), 10, info, expected_path=tempdir)
        self.useFixture(StaticLoaderFixture([backend]))
        write_packaging(tempdir)
        self.assertThat(tempdir, ControlHasSourceName(name))

    def test_write_packaging_passes_allowed_backend_names(self):
        name = PackageName.clean(self.getUniqueString())
        other_name = name + "WRONG"
        info1 = self.make_info(name)
        info2 = self.make_info(other_name)
        tempdir = self.useFixture(TempDir()).path
        backend1 = StaticBackend(
            self.getUniqueString(), 10, info1, expected_path=tempdir)
        backend2 = StaticBackend(
            self.getUniqueString(), 20, info2)
        self.useFixture(StaticLoaderFixture(
            [backend1, backend2]))
        write_packaging(tempdir, allowed_backend_names=[backend1.name])
        self.assertThat(tempdir, ControlHasSourceName(name))


class TestWritePackagingInformation(TestCase):

    def test_writes_packaging(self):
        path = self.useFixture(TempDir()).path
        package_name = PackageName.clean(self.getUniqueString())
        info = DictInfo(
            {
                PackageName.name: package_name,
                Maintainer.name: self.getUniqueString(),
                Architecture.name: "all",
                Description.name: self.getUniqueString(),
                Version.name: "1",
            })
        write_packaging_info(path, info)
        self.assertThat(path, ControlHasSourceName(package_name))
