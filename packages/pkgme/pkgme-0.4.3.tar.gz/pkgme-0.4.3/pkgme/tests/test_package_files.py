import datetime
import json
import os

from debian import changelog
from testtools import TestCase
from testtools.matchers import StartsWith
from treeshape import FileTree

from ..info_elements import (
    Architecture,
    ApplicationName,
    BuildDepends,
    Buildsystem,
    Categories,
    DebhelperAddons,
    debian_formatted_text,
    Depends,
    Description,
    Executable,
    ExplicitCopyright,
    ExtraControlBinaryFields,
    ExtraFiles,
    ExtraFilesFromPaths,
    ExtraTargets,
    Homepage,
    Icon,
    InfoElement,
    License,
    Maintainer,
    PackageName,
    Section,
    TagLine,
    Version,
    WorkingDirectory,
    )
from ..package_files import (
    BasicFile,
    Changelog,
    Compat,
    Control,
    Copyright,
    DEBIAN_DIR,
    Desktop,
    PackageFile,
    PackageFileGroup,
    SourceFormat,
    Rules,
    TemplatePackageFile,
    )
from ..project_info import DictInfo
from ..testing import (
    AreDesktopValuesFor,
    ControlStanzaHasField,
    ControlStanzaDoesntHaveField,
    ControlSourceStanzaHasField,
    ControlSourceStanzaDoesntHaveField,
    )


class TestElement1(InfoElement):

    name = "test_element_1"


class TestElement2(InfoElement):

    name = "test_element_2"


class TestPackageFile(PackageFile):

    elements = [
        TestElement1,
        TestElement2,
        ]


class PackageFileTestCase(TestCase):

    def get_default_args(self):
        return {}

    def get_object(self, other_args=None):
        args = self.get_default_args()
        if other_args is not None:
            args.update(other_args)
        return self.cls.from_info(DictInfo(args))

    def get_package_name(self):
        return PackageName.clean(self.getUniqueString())


class BasicFileTests(TestCase):

    def test_basic_file(self):
        f = BasicFile('foo/bar.txt', 'content')
        self.assertEqual('foo/bar.txt', f.path)
        self.assertEqual('content', f.get_contents())

    def test_default_overwrite(self):
        f = BasicFile('foo/bar.txt', 'content')
        self.assertEqual(True, f.overwrite)

    def test_specified_overwrite(self):
        f = BasicFile('foo/bar.txt', 'content', overwrite=False)
        self.assertEqual(False, f.overwrite)

    def test_default_elements(self):
        f = BasicFile('foo/bar.txt', 'content')
        self.assertEqual([], f.elements)

    def test_specified_elements(self):
        f = BasicFile('foo/bar.txt', 'content', elements=[TestElement2])
        self.assertEqual([TestElement2], f.elements)


class PackageFileTests(TestCase):

    def test_empty_by_default(self):
        package_file = PackageFile({})
        self.assertEqual("", package_file.get_contents())

    def test_overwrite_by_default(self):
        package_file = PackageFile({})
        self.assertEqual(True, package_file.overwrite)

    def test_from_info_returns_instance(self):
        package_file = PackageFile.from_info(None)
        self.assertIsInstance(package_file, PackageFile)

    def test_from_info_sets_values(self):
        package_file = PackageFile.from_info(None)
        self.assertEqual({}, package_file.values)

    def test_from_info_gets_values(self):
        value = self.getUniqueString()
        project_info = DictInfo({TestElement1.name: value})
        package_file = TestPackageFile.from_info(project_info)
        self.assertEqual(
            {
                TestElement1.name: value,
                TestElement2.name: None,
            }, package_file.values)


class TestTemplatePackageFile(TemplatePackageFile):

    template = "test_dummy"


class TemplatePackageFileTests(TestCase):

    def test_get_contents(self):
        package_file = TestTemplatePackageFile({"var": "foo"})
        self.assertIn("TEST DUMMY", package_file.get_contents())


class CompatTests(PackageFileTestCase):

    cls = Compat

    def test_path(self):
        package_file = self.get_object()
        self.assertEqual(
            os.path.join(DEBIAN_DIR, "compat"), package_file.path)

    def test_contents(self):
        package_file = self.get_object()
        self.assertEqual("7\n", package_file.get_contents())

    def test_overwrite(self):
        package_file = self.get_object()
        self.assertEqual(True, package_file.overwrite)


class RulesTests(PackageFileTestCase):

    cls = Rules

    def get_default_args(self):
        return {
            Buildsystem.name: None,
            }

    def test_path(self):
        package_file = self.get_object()
        self.assertEqual(
            os.path.join(DEBIAN_DIR, "rules"), package_file.path)

    def test_contents_is_a_makefile(self):
        package_file = self.get_object()
        self.assertThat(
            package_file.get_contents(),
            StartsWith("#!/usr/bin/make -f\n"))

    def test_contents_contains_dh_call(self):
        package_file = self.get_object()
        self.assertIn("%:\n\tdh $@ \n", package_file.get_contents())

    def test_contents_with_buildsystem(self):
        buildsystem = self.getUniqueString()
        args = {Buildsystem.name: buildsystem}
        package_file = self.get_object(args)
        self.assertIn(
            "%%:\n\tdh $@ --buildsystem=%s \n" % buildsystem,
            package_file.get_contents())

    def test_content_with_debhelper_addons(self):
        debhelper_addons = self.getUniqueString()
        args = {DebhelperAddons.name: debhelper_addons}
        package_file = self.get_object(args)
        self.assertIn(
            "%%:\n\tdh $@ --with=%s \n" % debhelper_addons,
            package_file.get_contents())

    def test_content_with_extra_targets(self):
        extra_targets = """
include /usr/share/cli-common/cli.make

override_dh_auto_build:
	xbuild $(CURDIR)/WideMargin.sln /p:Configuration=Release

override_dh_auto_clean:
	xbuild $(CURDIR)/WideMargin.sln /p:Configuration=Release /t:Clean
"""
        args = {ExtraTargets.name: extra_targets}
        package_file = self.get_object(args)
        self.assertIn(extra_targets, package_file.get_contents())

    def test_overwrite(self):
        package_file = self.get_object()
        self.assertEqual(True, package_file.overwrite)


class CopyrightTests(PackageFileTestCase):

    cls = Copyright

    def get_default_args(self):
        return { PackageName.name: "somepackage",
                 Maintainer.name: "Random Guy <foo@example.com>",
                 License.name: 'BSD',
               }

    def test_path(self):
        package_file = self.get_object()
        self.assertEqual(
            os.path.join(DEBIAN_DIR, "copyright"), package_file.path)

    def test_copyright_valid(self):
        package_file = self.get_object()
        self.assertEqual(package_file.get_contents(),
"""Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: somepackage
Upstream-Contact: Random Guy <foo@example.com>

Files: *
Copyright: %(year)s Random Guy <foo@example.com>
License: BSD
 The full text of the can be found in the file '/usr/share/common-licenses/BSD'.

Files: debian/*
Copyright: %(year)s The friendly pkgme.net robot
License: public-domain
""" % {'year' : datetime.datetime.now().year,})

    def test_explicit_copyright(self):
        package_file = self.get_object(
            {ExplicitCopyright.name: "blah blah blah",
             License.name: 'proprietary',
            })
        self.assertEqual(package_file.get_contents(),
                         """\
Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: somepackage
Upstream-Contact: Random Guy <foo@example.com>

Files: *
Copyright: blah blah blah
License: proprietary

Files: debian/*
Copyright: %(year)s The friendly pkgme.net robot
License: public-domain
""" % {'year' : datetime.datetime.now().year,})

    def test_explicit_copyright_multiline(self):
        copyright_msg = """\
Please see the enclosed PDF file for the exact copyright holders or contact the submitter of the application '%(submitter)s'

This file was automatically generated.
""" % {'submitter': 'Arthur Dent <arthur.dent@canonical.com'}
        package_file = self.get_object(
            {ExplicitCopyright.name: copyright_msg,
             License.name: 'proprietary',
            })
        self.assertEqual(package_file.get_contents(),
                         """\
Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: somepackage
Upstream-Contact: Random Guy <foo@example.com>

Files: *
Copyright: %(clean_copyright)s
License: proprietary

Files: debian/*
Copyright: %(year)s The friendly pkgme.net robot
License: public-domain
""" % {'year' : datetime.datetime.now().year,
       'clean_copyright': debian_formatted_text(copyright_msg),
       })

    def test_overwrite(self):
        package_file = self.get_object()
        self.assertEqual(True, package_file.overwrite)


class ChangelogTests(PackageFileTestCase):

    cls = Changelog

    def get_default_args(self):
        return {
            Maintainer.name: "Maintainer <someone@example.org>",
            PackageName.name: "somepackage",
            Version.name: "1",
            }

    def test_path(self):
        package_file = self.get_object()
        self.assertEqual(
            os.path.join(DEBIAN_DIR, "changelog"), package_file.path)

    def test_contents_contains_version(self):
        version = "123"
        args = {Version.name: version}
        package_file = self.get_object(args)
        contents = package_file.get_contents()
        stanza = changelog.Changelog(contents)
        self.assertEqual(changelog.Version(version), stanza.version)

    def test_overwrite(self):
        package_file = self.get_object()
        self.assertEqual(True, package_file.overwrite)


class ControlTests(PackageFileTestCase):

    cls = Control

    def get_default_args(self):
        return {
            PackageName.name: self.getUniqueString(),
            Section.name: self.getUniqueString(),
            Maintainer.name: self.getUniqueString(),
            Homepage.name: None,
            BuildDepends.name: None,
            Architecture.name: "all",
            Depends.name: None,
            Description.name: self.getUniqueString(),
            }

    def test_path(self):
        package_file = self.get_object()
        self.assertEqual(
            os.path.join(DEBIAN_DIR, "control"), package_file.path)

    def test_overwrite(self):
        package_file = self.get_object()
        self.assertEqual(True, package_file.overwrite)

    def test_get_contents_sets_package_name(self):
        package_name = self.get_package_name()
        args = {PackageName.name: package_name}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlSourceStanzaHasField("Source", package_name))

    def test_get_contents_sets_binary_package_name(self):
        package_name = self.get_package_name()
        args = {PackageName.name: package_name}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlStanzaHasField(1, "Package", package_name))

    def test_get_contents_sets_section(self):
        section = self.getUniqueString()
        args = {Section.name: section}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlSourceStanzaHasField("Section", section))

    def test_get_contents_sets_binary_section(self):
        section = self.getUniqueString()
        args = {Section.name: section}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlStanzaHasField(1, "Section", section))

    def test_get_contents_sets_priority(self):
        package_file = self.get_object()
        self.assertThat(
            package_file.get_contents(),
            ControlSourceStanzaHasField("Priority", "extra"))

    def test_get_contents_sets_binary_priority(self):
        package_file = self.get_object()
        self.assertThat(
            package_file.get_contents(),
            ControlStanzaHasField(1, "Priority", "extra"))

    def test_get_contents_sets_maintainer(self):
        maintainer = "%s <dude@example.com>" % (self.getUniqueString(),)
        args = {Maintainer.name: maintainer}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlSourceStanzaHasField("Maintainer", maintainer))

    def test_get_contents_sets_homepage(self):
        homepage = self.getUniqueString()
        args = {Homepage.name: homepage}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlSourceStanzaHasField("Homepage", homepage))

    def test_get_contents_without_homepage(self):
        args = {Homepage.name: None}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlSourceStanzaDoesntHaveField("Homepage"))

    def test_get_contents_sets_build_depends(self):
        build_depends = self.getUniqueString()
        build_depends = BuildDepends.clean(build_depends)
        args = {BuildDepends.name: build_depends}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlSourceStanzaHasField("Build-Depends", build_depends))

    def test_get_contents_sets_architecture(self):
        architecture = self.getUniqueString()
        args = {Architecture.name: architecture}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlStanzaHasField(1, "Architecture", architecture))

    def test_get_contents_sets_depends(self):
        depends = self.getUniqueString()
        args = {Depends.name: depends}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlStanzaHasField(1, "Depends", depends))

    def test_get_contents_without_depends(self):
        args = {Depends.name: None}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlStanzaDoesntHaveField(1, "Depends"))

    def test_get_contents_sets_description(self):
        description = self.getUniqueString()
        args = {Description.name: description}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlStanzaHasField(1, "Description", description))

    def test_get_contents_sets_any_extra_binary_fields(self):
        extra_field_name1 = "X-{}".format(self.getUniqueString())
        extra_field_name2 = "X-{}".format(self.getUniqueString())
        extra_field_value1 = self.getUniqueString()
        extra_field_value2 = self.getUniqueString()
        extra_fields = "{0}: {1}\n{2}: {3}".format(
            extra_field_name1, extra_field_value1,
            extra_field_name2, extra_field_value2)
        args = {ExtraControlBinaryFields.name: extra_fields}
        package_file = self.get_object(args)
        self.assertThat(
            package_file.get_contents(),
            ControlStanzaHasField(1, extra_field_name1,
                extra_field_value1))
        self.assertThat(
            package_file.get_contents(),
            ControlStanzaHasField(1, extra_field_name2,
                extra_field_value2))


class SourceFormatTests(PackageFileTestCase):

    cls = SourceFormat

    def get_default_args(self):
        return {}

    def test_path(self):
        package_file = self.get_object()
        self.assertEqual(
            os.path.join(DEBIAN_DIR, "source/format"), package_file.path)

    def test_contents(self):
        package_file = self.get_object()
        self.assertEqual("3.0 (quilt)\n", package_file.get_contents())

    def test_overwrite(self):
        package_file = self.get_object()
        self.assertEqual(True, package_file.overwrite)


class DesktopFileTests(PackageFileTestCase):

    cls = Desktop

    def get_default_args(self):
        return {
            Executable.name: '/opt/whatever/bin/whatever',
            PackageName.name: 'whatever',
            }

    def test_path(self):
        package_name = self.get_package_name()
        package_file = self.get_object({PackageName.name: package_name})
        self.assertEqual('%s.desktop' % package_name, package_file.path)

    def test_core_values(self):
        # The desktop file is for an application, and is in the 1.0 format of
        # the specification.
        package_file = self.get_object()
        self.assertThat(
            {'Type': 'Application', 'Version': '1.0'},
            AreDesktopValuesFor(package_file))

    def test_name(self):
        # The name in the desktop file is a human-readable application name.
        app_name = self.getUniqueString()
        package_file = self.get_object({ApplicationName.name: app_name})
        self.assertThat({'Name': app_name}, AreDesktopValuesFor(package_file))

    def test_categories(self):
        categories = self.getUniqueString()
        package_file = self.get_object({Categories.name: categories})
        self.assertThat({'Categories': categories}, AreDesktopValuesFor(package_file))

    def test_executable(self):
        executable = self.getUniqueString()
        package_file = self.get_object({Executable.name: executable})
        self.assertThat({'Exec': executable}, AreDesktopValuesFor(package_file))

    def test_icon(self):
        icon = self.getUniqueString()
        package_file = self.get_object({Icon.name: icon})
        self.assertThat({'Icon': icon}, AreDesktopValuesFor(package_file))

    def test_tagline(self):
        # The tagline from the metadata becomes the comment in the desktop file.
        tagline = self.getUniqueString()
        package_file = self.get_object({TagLine.name: tagline})
        self.assertThat({'Comment': tagline}, AreDesktopValuesFor(package_file))

    def test_working_dir(self):
        # The WorkingDirectory is set as Path in the desktop file
        working_directory = self.getUniqueString()
        package_file = self.get_object({WorkingDirectory.name: working_directory})
        self.assertThat({'Path': working_directory}, AreDesktopValuesFor(package_file))


class PackageFileGroupTests(TestCase):

    def test_add_file_cls(self):
        group = PackageFileGroup()
        group.add_file_cls(TestPackageFile)
        self.assertEqual([TestPackageFile], group.files_cls)

    def test_get_files(self):
        group = PackageFileGroup()
        group.add_file_cls(TestPackageFile)
        group.add_file_cls(TestPackageFile)
        value = self.getUniqueString()
        project_info = DictInfo({TestElement1.name: value})
        files = group.get_files(project_info)
        self.assertEqual(2, len(files))
        self.assertIsInstance(files[0], TestPackageFile)
        self.assertIsInstance(files[1], TestPackageFile)
        self.assertEqual(value, files[0].values[TestElement1.name])
        self.assertEqual(value, files[1].values[TestElement1.name])

    def test_get_elements(self):
        group = PackageFileGroup()
        group.add_file_cls(TestPackageFile)
        group.add_file_cls(TestPackageFile)
        self.assertEqual(
            set([TestElement1, TestElement2]), group.get_elements())

    def test_extra_files(self):
        group = PackageFileGroup()
        project_info = DictInfo({
            ExtraFiles.name: {
                'foo.txt': "Hello world!\n",
                'debian/install': "Bwawahahaha\n",
                }})
        files = group.get_files(project_info)
        [foo, install] = files
        self.assertEqual('foo.txt', foo.path)
        self.assertEqual("Hello world!\n", foo.get_contents())
        self.assertEqual(True, foo.overwrite)

    def test_extra_files_from_json(self):
        group = PackageFileGroup()
        project_info = DictInfo({
            ExtraFiles.name: json.dumps({
                'foo.txt': "Hello world!\n",
                'debian/install': "Bwawahahaha\n",
                })})
        files = group.get_files(project_info)
        [foo, install] = files
        self.assertEqual('foo.txt', foo.path)
        self.assertEqual("Hello world!\n", foo.get_contents())
        self.assertEqual(True, foo.overwrite)

    def test_extra_files_from_paths(self):
        foo_content = self.getUniqueString()
        tree = self.useFixture(
            FileTree(
                {'foo': {'content': foo_content},
                 'bar': {}}))
        group = PackageFileGroup()
        project_info = DictInfo({
            ExtraFilesFromPaths.name: {
                'foo.txt': tree.join('foo'),
                'debian/install': tree.join('bar'),
                }})
        files = group.get_files(project_info)
        [foo, install] = files
        self.assertEqual('foo.txt', foo.path)
        self.assertEqual(foo_content, foo.get_contents())
        self.assertEqual(True, foo.overwrite)

    def test_get_info_once(self):
        foo_content = self.getUniqueString()
        tree = self.useFixture(
            FileTree(
                {'foo': {'content': foo_content},
                 'bar': {}}))
        group = PackageFileGroup()
        project_info = DictInfo({
            ExtraFilesFromPaths.name: {
                'foo.txt': tree.join('foo'),
                'debian/install': tree.join('bar'),
                }})
        calls = []
        orig_get_all = project_info.get_all
        def get_all(keys):
            calls.append(keys)
            return orig_get_all(keys)
        project_info.get_all = get_all
        group.get_files(project_info)
        self.assertEqual(1, len(calls), calls)
