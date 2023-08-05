from ConfigParser import ConfigParser
import os
from StringIO import StringIO
import subprocess

from debian import deb822
from fixtures import (
    Fixture,
    TempDir,
    )
from testtools.matchers import (
    Equals,
    Matcher,
    Mismatch,
    MismatchesAll,
    )

from pkgme.backend import (
    StaticLoader,
    set_default_loader_factory,
    reset_default_loader_factory,
    )
from pkgme.write import write_file


class TempdirFixture(TempDir):
    """DEPRECATED - Use ``treeshape.FileTree`` instead."""

    def abspath(self, relpath):
        return os.path.abspath(os.path.join(self.path, relpath))

    def touch(self, relpath, mode=None):
        """Create the file at 'relpath' with no content."""
        self.create_file(relpath, '')
        if mode:
            os.chmod(self.abspath(relpath), mode)

    def create_file(self, relpath, content):
        """Create the file at 'relpath' with 'content'."""
        write_file(self.abspath(relpath), content)

    def mkdir(self, relpath):
        """Make a directory at 'relpath'."""
        path = self.abspath(relpath)
        os.mkdir(path)
        return path

    def __repr__(self):
        return '<TempdirFixture: {0}>'.format(self.path)


class FileFixture(Fixture):
    """DEPRECATED - Use ``treeshape.FileTree`` instead."""

    def __init__(self, path, contents):
        super(FileFixture, self).__init__()
        self.path = path
        self.contents = contents

    def setUp(self):
        Fixture.setUp(self)
        with open(self.path, "w") as f:
            f.write(self.contents)
        self.addCleanup(os.unlink, self.path)


class ExecutableFileFixture(FileFixture):
    """DEPRECATED - Use ``treeshape.FileTree`` instead."""

    def setUp(self):
        FileFixture.setUp(self)
        os.chmod(self.path, 0700)


class NotAControlFileMismatch(Mismatch):

    def describe(self):
        return "Is not a control file"


class NotEnoughStanzasMismatch(Mismatch):

    def describe(self):
        return "doesn't have enough stanzas"


class ControlStanzaHasField(Matcher):

    def __init__(self, stanza, key, value):
        self.stanza = stanza
        self.key = key
        self.value = value

    def match(self, matchee):
        i = 0
        for source_stanza in deb822.Deb822.iter_paragraphs(
            matchee.splitlines()):
            if i == self.stanza:
                if self.key not in source_stanza:
                    return HasNoKeyMismatch(self.key)
                return Equals(self.value).match(source_stanza[self.key])
            i += 1
        if i < 1:
            return NotAControlFileMismatch()
        return NotEnoughStanzasMismatch()

    def __str__(self):
        return (
            "is a control file with %s: %s in the %dth stanza."
            % (self.key, self.value, self.stanza))


class ControlSourceStanzaHasField(ControlStanzaHasField):

    def __init__(self, key, value):
        super(ControlSourceStanzaHasField, self).__init__(0, key, value)


class ControlStanzaDoesntHaveField(Matcher):

    def __init__(self, stanza, key):
        self.stanza = stanza
        self.key = key

    def match(self, matchee):
        i = 0
        for source_stanza in deb822.Deb822.iter_paragraphs(
            matchee.splitlines()):
            if i == self.stanza:
                if self.key in source_stanza:
                    return HasKeyMismatch(self.key)
                return None
            i += 1
        if i < 1:
            return NotAControlFileMismatch()
        return NotEnoughStanzasMismatch()

    def __str__(self):
        return (
            "is a control file with no %s in the %dth stanza."
            % (self.key, self.stanza))


class ControlSourceStanzaDoesntHaveField(ControlStanzaDoesntHaveField):

    def __init__(self, key):
        super(ControlSourceStanzaDoesntHaveField, self).__init__(0, key)


class HasNoKeyMismatch(Mismatch):

    def __init__(self, key):
        self.key = key

    def describe(self):
        return "Has no key %s" % self.key


class HasKeyMismatch(Mismatch):

    def __init__(self, key):
        self.key = key

    def describe(self):
        return "Has key %s" % self.key


class DictContains(Matcher):
    """Matches dicts that contain the given dict."""

    def __init__(self, inner_dict):
        self.inner_dict = inner_dict

    def match(self, outer_dict):
        inner_dict = self.inner_dict
        mismatches = []
        for key in inner_dict:
            if key not in outer_dict:
                mismatches.append(HasNoKeyMismatch(key))
            else:
                equal = Equals(inner_dict[key]).match(outer_dict[key])
                if equal:
                    mismatches.append(equal)
        if mismatches:
            return MismatchesAll(mismatches)


class AreDesktopValuesFor(Matcher):

    def __init__(self, package_file):
        self.package_file = package_file

    def __str__(self):
        return 'AreDesktopValuesFor(%s)' % (self.package_file,)

    def match(self, expected_values):
        parser = ConfigParser()
        # Keys are case-sensitive.
        # <http://docs.python.org/release/2.6.5/library/configparser.html>
        parser.optionxform = str
        parser.readfp(StringIO(self.package_file.get_contents()))
        data = dict(parser.items('Desktop Entry'))
        return DictContains(expected_values).match(data)


def require_command(command_name):
    """Check to see if the named command exists.

    :param command_name: The name of the command to check.
    :return: None if the command exists, a string describing the failure if it
        does not.
    """
    try:
        subprocess.call(command_name)
    except OSError as error:
        # Assume command not found.
        return str(error)
    else:
        return None


class CommandRequiredTestCase(object):

    def skipTestIfCommandNotExecutable(self, command_name):
        """Skip the test if a particular command can't be run.

        Try running the passed command, and if it fails then skip the test.
        :param command_name: the name of the command to check
        :return: None
        :raises: TestSkipped if command_name can't be run.
        """
        find_error = require_command(command_name)
        if find_error is not None:
            self.skipTest("'%s' not executable: %s" % (command_name, find_error))


class PathRequiredTestCase(object):

    def skipTestIfPathNotPresent(self, path):
        """Skip the test if a particular path doesn't exist.

        :param path: the path that must exist
        :return: None
        :raises: TestSkipped if path isn't present
        """
        if not os.path.exists(path):
            self.skipTest("'%s' not present" % (path, ))


class StaticLoaderFixture(Fixture):
    """Change the default loader to one that only loads the given backends."""

    def __init__(self, backends):
        """Construct a ``StaticLoaderFixture``.

        :param backends: A list of backends for the loader to load.
        """
        self.backends = backends

    def setUp(self):
        super(StaticLoaderFixture, self).setUp()
        self.addCleanup(reset_default_loader_factory)
        set_default_loader_factory(self.make_loader)

    def make_loader(self):
        return StaticLoader(self.backends)
