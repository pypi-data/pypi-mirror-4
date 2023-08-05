#!/usr/bin/python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# © 2010 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Michael Terry <michael.terry@canonical.com>
# =====================================================================

from fixtures import TempDir
from testtools import TestCase
from treeshape import FileTree, from_rough_spec

from ..backend import ExternalHelpersBackend, get_backend_dir
from ..testing import CommandRequiredTestCase


backend_dir = get_backend_dir(__file__, 'vala')


class ValaBackendTests(TestCase, CommandRequiredTestCase):

    def make_tree(self, *spec):
        return self.useFixture(FileTree(from_rough_spec(spec)))

    def get_backend(self):
        return ExternalHelpersBackend("vala", backend_dir)

    def test_want_zero_deep(self):
        tempdir = self.make_tree('configure.ac', 'main.vala')
        backend = self.get_backend()
        self.assertEqual((20, None), backend.want(tempdir.path))

    def test_want_one_deep(self):
        tempdir = self.make_tree("configure.ac", "one/main.vala")
        backend = self.get_backend()
        self.assertEqual((20, None), backend.want(tempdir.path))

    def test_want_two_deep(self):
        tempdir = self.make_tree("configure.ac", "one/two/main.vala")
        backend = self.get_backend()
        self.assertEqual((0, None), backend.want(tempdir.path))

    def test_want_without_configure_ac(self):
        tempdir = self.make_tree("main.vala")
        backend = self.get_backend()
        self.assertEqual((0, None), backend.want(tempdir.path))

    def test_want_with_configure_in(self):
        tempdir = self.make_tree("main.vala", "configure.in")
        backend = self.get_backend()
        self.assertEqual((20, None), backend.want(tempdir.path))

    def test_architecture(self):
        tempdir = self.useFixture(TempDir())
        info = self.get_backend().get_info(tempdir.path)
        self.assertEqual(
            {"architecture": "any"}, info.get_all(["architecture"]))

    def test_buildsystem(self):
        tempdir = self.useFixture(TempDir())
        info = self.get_backend().get_info(tempdir.path)
        self.assertEqual(
            {"buildsystem": "autoconf"}, info.get_all(["buildsystem"]))

    def test_build_depends(self):
        self.skipTestIfCommandNotExecutable('vala-dep-scanner')
        tempdir = self.make_tree(("main.vala", "Gtk.Window win;"))
        info = self.get_backend().get_info(tempdir.path)
        self.assertEqual(
            {"build_depends": "libgtk3.0-dev, valac"},
            info.get_all(["build_depends"]))

    def test_depends(self):
        tempdir = self.useFixture(TempDir())
        info = self.get_backend().get_info(tempdir.path)
        self.assertEqual(
            {"depends": "${shlibs:Depends}"}, info.get_all(["depends"]))

    def test_homepage(self):
        tempdir = self.make_tree(
            ("configure.ac",
             "AC_INIT([Example Project],[1.0],[http://bugs.example.com/],"
             "[example-project], [http://example.com/] )"))
        info = self.get_backend().get_info(tempdir.path)
        self.assertEqual(
            {"homepage": "http://example.com/"}, info.get_all(["homepage"]))

    def test_homepage_none(self):
        tempdir = self.make_tree(
            ("configure.ac",
             "AC_INIT([Example Project],[1.0],[http://bugs.example.com/],"
             "[example-project])"))
        info = self.get_backend().get_info(tempdir.path)
        self.assertEqual(
            {"homepage": ""}, info.get_all(["homepage"]))

    def test_package_name(self):
        tempdir = self.make_tree(
            ("configure.ac",
             "AC_INIT([GNU Example Project],[1.0],[http://bugs.example.com/],"
             "[co ol-proj],[http://example.com/])"))
        info = self.get_backend().get_info(tempdir.path)
        self.assertEqual(
            {"package_name": "co ol-proj"}, info.get_all(["package_name"]))

    def test_package_name_none(self):
        tempdir = self.make_tree(
            ("configure.ac",
             "AC_INIT( [GNU Example Project] , [1.0],"
             "[http://bugs.example.com/])"))
        info = self.get_backend().get_info(tempdir.path)
        self.assertEqual(
            {"package_name": "example-project"}, info.get_all(["package_name"]))
