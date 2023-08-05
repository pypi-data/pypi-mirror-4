import datetime
import os

from testtools import try_imports

# In lucid, python-debian exports its package as 'debian_bundle'.
changelog = try_imports(['debian.changelog', 'debian_bundle.changelog'])

from pkgme.info_elements import (
    ApplicationName,
    Architecture,
    BuildDepends,
    Buildsystem,
    Categories,
    DebhelperAddons,
    Depends,
    Description,
    Distribution,
    Executable,
    ExplicitCopyright,
    ExtraControlBinaryFields,
    ExtraFiles,
    ExtraFilesFromPaths,
    ExtraTargets,
    Homepage,
    Icon,
    License,
    Maintainer,
    PackageName,
    Section,
    TagLine,
    Version,
    WorkingDirectory,
    )
from pkgme.project_info import DictInfo
from pkgme.template_file import TemplateFile


DEBIAN_DIR = "debian"


class BasicFile(object):

    def __init__(self, path, content, overwrite=True, elements=None):
        self.path = path
        self._content = content
        self.overwrite = overwrite
        if elements is None:
            elements = []
        self.elements = elements

    def get_contents(self):
        return self._content


class FileFromDisk(object):
    """A file that takes its contents from a file on disk."""

    def __init__(self, target_path, source_path, overwrite=True, elements=None):
        """Create a FileFromDisk.

        :param target_path: the path that the file should be written to.
        :param source_path: the path that the contents should be read from.
        :param overwrite: whether to overwrite the target file if it is
            present. Default is True.
        :param elements: The InfoElements needed for the content of this
            file. Default is None meaning no elements.
        """
        self.path = target_path
        self.source_path = source_path
        self.overwrite = overwrite
        if elements is None:
            elements = []
        self.elements = elements

    def get_contents(self):
        with open(self.source_path) as f:
            return f.read()


class PackageFile(object):

    overwrite = True

    def __init__(self, values):
        self.values = values

    def get_contents(self):
        return ""

    @classmethod
    def from_info(cls, project_info):
        elements = getattr(cls, "elements", [])
        values = {}
        for element in elements:
            values[element.name] = element.get_value(project_info)
        return cls(values)


class TemplatePackageFile(PackageFile):

    def get_contents(self):
        t = TemplateFile(self.template)
        return t.render(self.values)


class DebianPackageFile(PackageFile):

    @property
    def path(self):
        return os.path.join(DEBIAN_DIR, self.filename)


class PackageFileGroup(object):

    def __init__(self):
        self.files_cls = []

    def add_file_cls(self, package_file_cls):
        self.files_cls.append(package_file_cls)

    def get_files(self, project_info):
        elements = self.get_elements()
        # XXX: Kind of hacky.  The thing is that the ExtraFiles element isn't
        # an informational element used by key files, but rather a way of
        # forcing extra files to be written.
        keys = (
            [ExtraFiles.name] + [ExtraFilesFromPaths.name]
            + [element.name for element in elements])
        values = project_info.get_all(keys)
        new_info = DictInfo(values)
        files = []
        for file_cls in self.files_cls:
            files.append(file_cls.from_info(new_info))
        extra_files = ExtraFiles.get_value(project_info)
        for path, contents in extra_files.items():
            files.append(BasicFile(path, contents))
        extra_files = ExtraFilesFromPaths.get_value(project_info)
        for target_path, source_path in extra_files.items():
            files.append(FileFromDisk(target_path, source_path))
        return files

    def get_elements(self):
        elements = set()
        for file_cls in self.files_cls:
            file_elements = getattr(file_cls, "elements", [])
            for element in file_elements:
                elements.add(element)
        return elements


default_package_file_group = PackageFileGroup()


class Compat(DebianPackageFile):

    filename = "compat"

    def get_contents(self):
        return "7\n"


default_package_file_group.add_file_cls(Compat)


class Rules(DebianPackageFile, TemplatePackageFile):

    elements = [
        Buildsystem,
        DebhelperAddons,
        ExtraTargets,
        ]

    filename = "rules"
    template = "rules"


default_package_file_group.add_file_cls(Rules)


class Copyright(DebianPackageFile, TemplatePackageFile):

    # See http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/

    elements = [
        ExplicitCopyright,
        PackageName,
        License,
        Homepage,
        Maintainer,
        ]
    filename = 'copyright'
    template = 'copyright'


default_package_file_group.add_file_cls(Copyright)


class Changelog(DebianPackageFile):

    elements = [
        PackageName,
        Distribution,
        Version,
        Maintainer,
        ]

    filename = "changelog"

    def get_contents(self):
        cl = changelog.Changelog()
        cl.new_block(
            package=self.values[PackageName.name],
            version=self.values[Version.name],
            distributions=self.values[Distribution.name],
            changes=["", "  * Initial release", ""],
            author=self.values[Maintainer.name],
            date=datetime.datetime.utcnow().strftime(
                "%a, %d %b %Y %H:%M:%S +0000"),
            urgency="low",
            )
        return str(cl)


default_package_file_group.add_file_cls(Changelog)


class Control(DebianPackageFile, TemplatePackageFile):

    elements = [
        Architecture,
        BuildDepends,
        Depends,
        Description,
        ExtraControlBinaryFields,
        Homepage,
        Maintainer,
        PackageName,
        Section,
        ]

    filename = "control"
    template = "control"


default_package_file_group.add_file_cls(Control)


class SourceFormat(DebianPackageFile):

    elements = []

    filename = "source/format"

    def get_contents(self):
        return "3.0 (quilt)\n"


default_package_file_group.add_file_cls(SourceFormat)


class Desktop(TemplatePackageFile):

    # See http://standards.freedesktop.org/desktop-entry-spec/latest/ar01s05.html

    elements = [
        ApplicationName,
        Categories,
        Executable,
        Icon,
        PackageName,
        TagLine,
        WorkingDirectory,
        ]

    template = 'desktop'

    @property
    def path(self):
        return '%s.desktop' % (self.values[PackageName.name],)


