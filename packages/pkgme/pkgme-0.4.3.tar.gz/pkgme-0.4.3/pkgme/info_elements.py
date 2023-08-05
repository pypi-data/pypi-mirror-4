import errno
import json
import re
import rfc822
import os


class InvalidInfoError(Exception):
    pass

class MissingInfoError(Exception):
    pass


class InfoElement(object):

    required = False
    default = None

    @property
    def name(self):
        raise NotImplementedError(
            "Define a name attribute on %s" % self.__class__)

    @property
    def description(self):
        raise NotImplementedError(
            "Define a name attribute on %s" % self.__class__)

    @classmethod
    def get_default(cls):
        """Get the default value for this InfoElement.

        By default, returns the 'default' class variable.  Override this
        method only if you want to do something special to figure out your
        default.
        """
        return cls.default

    @classmethod
    def get_value(cls, info):
        vals = info.get_all([cls.name])
        val = vals.get(cls.name, None)
        if val is None:
            if cls.required:
                raise MissingInfoError(
                    "The backend didn't provide a value for '%s'" % cls.name)
            val = cls.get_default()
        val = cls.clean(val)
        return val

    @classmethod
    def clean(cls, value):
        """Validate and modify the value as needed.

        This method should do any validation needed on the value. It can also
        modify the value if needed. It should return the new value or the
        passed value if there is nothing to do.
        """
        return value


class Buildsystem(InfoElement):

    name = "buildsystem"
    description = "The debhelper buildsystem to use to build the package."


class ExtraTargets(InfoElement):

    name = 'extra_targets'
    description = "Extra targets for the 'rules' file."


class PackageName(InfoElement):

    name = "package_name"
    description = "The name of the package."
    required = True

    @classmethod
    def clean(cls, value):
        # Package names (both source and binary, see Package, Section 5.6.7)
        # must consist only of lower case letters (a-z), digits (0-9), plus
        # (+) and minus (-) signs, and periods (.). They must be at least two
        # characters long and must start with an alphanumeric character.
        #
        # http://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Source
        cleaned = value.lower()
        cleaned = re.sub(r'[^a-z0-9+.-]', '', cleaned)
        cleaned = cleaned.lstrip('.+-')
        if len(cleaned) < 2:
            raise InvalidInfoError(
                "Package name must be at least two characters long: %r"
                % (value,))
        return cleaned


class Section(InfoElement):

    name = "section"
    description = "The section the source package should go in."
    default = "misc"


class Maintainer(InfoElement):

    name = "maintainer"
    description = """The maintainer of the package.

    Should be in the form::

        Name <email>

    """

    default = "A Person <someone@example.com>"

    @classmethod
    def get_default(cls):
        return os.environ.get('DEBEMAIL', cls.default)

    @classmethod
    def clean(cls, value):
        name, email = rfc822.parseaddr(value)
        if not name:
            name = email
        if '@' not in email:
            email = 'person@example.com'
        maintainer = "%s <%s>" % (name, email)
        # Check that we get a valid result in all cases
        name, email = rfc822.parseaddr(maintainer)
        if name is None or email is None:
            raise AssertionError("Invalid maintainer format: %s" % maintainer)
        return maintainer


class Homepage(InfoElement):

    name = "homepage"
    description = """The homepage for the project.

    The URL of the website for the project.
    """


class Distribution(InfoElement):

    name = 'distribution'
    description = """The distribution to upload to.

    e.g. 'unstable', 'natty', 'oneiric'.
    """

    LSB_RELEASE = '/etc/lsb-release'

    @classmethod
    def get_default(cls):
        try:
            with open(cls.LSB_RELEASE) as fp:
                release_keys = dict(
                    line.strip().split('=') for line in fp.readlines())
            return release_keys['DISTRIB_CODENAME']
        except IOError, e:
            if e.errno == errno.ENOENT:
                return 'UNRELEASED'
            raise


class BuildDepends(InfoElement):

    name = "build_depends"
    description = """The build dependencies of the package."""

    @classmethod
    def clean(cls, value):
        if value is None:
            parts = []
        elif isinstance(value, (str, unicode)):
            parts = [value]
        else:
            parts = value
        # FIXME: should replace if the dependency isn't strict
        # enough
        # FIXME: check is too lax, needs to parse and compare package
        # names
        if not filter(lambda x: "debhelper" in x, parts):
            parts += ["debhelper (>= 7)"]
        return ", ".join(parts)


class DebhelperAddons(InfoElement):

    name = "debhelper_addons"
    description = """The debhelper addons to use."""


class Architecture(InfoElement):

    name = "architecture"
    description = """The architecture(s) to build the binary package for.

    This can be one of the following.

    any
        to build on every architecture (arch-dependent).
    all
        to build once and use the result on all architecture
        (arch-independent).
    a list of architectures (arch-dependent)
        to build on specific architectures only.

    """
    default = "any"


class Depends(InfoElement):

    name = "depends"
    description = """The dependencies of the binary package."""


def chomp(text):
    """Remove the trailing newline if present.

    Named after the Perl built-in that does the same thing.
    """
    # XXX: This is unused in pkgme, can we delete it? -- jml
    if text and text[-1] == '\n':
        return text[:-1]
    return text



def _format_lines(lines):
    first_line, lines = lines[0], lines[1:]
    yield first_line
    for i, line in enumerate(lines):
        is_blank = bool(not line.strip())
        if is_blank:
            yield ' .'
        elif line[0] == ' ':
            yield line
        else:
            yield ' ' + line


def debian_formatted_text(user_text):
    """Prepare ``user_text`` as Debian formatted text.

    If ``user_text`` looks to already be formatted according to Debian policy,
    then we pass it through.  If it does not, then we do our best to clean it
    up.

    We determine whether ``user_text`` is already Debian-formatted by checking
    whether the second line is indented by a space. If so, then we assume it's
    Debian-formatted.  If later lines break Debian formatting, then we raise a
    ValueError.

    This style of formatting is used for the Description field of the
    ``debian/control`` file, and for various fields in the
    ``debian/copyright`` file.

    See also:
    * http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/#file-syntax
    * http://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Description

    :param user_text: A string to be formatted as text for Debian files.
    :raise ValueError: When the string initially looks to be Debian-formatted
        but actually is not.
    :return: A correctly formatted version of that string.
    """
    if isinstance(user_text, unicode):
        user_text = user_text.encode('utf-8')
    if not user_text.strip():
        return ''
    return '\n'.join(_format_lines(user_text.strip().splitlines()))


class Description(InfoElement):

    name = "description"
    description = "The description of the package."
    default = "a package"

    @classmethod
    def clean(cls, value):
        """Prepare a string for the Description field in the control file.

        See http://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Description
        for the rules governing the Description field.

        :param value: A string to go into the Description field of a control
            file.
        :raise ValueError: When the string initially looks to be Debian-
            formatted but actually is not.
        :return: A correctly formatted version of that string.
        """
        return debian_formatted_text(value)


class Version(InfoElement):

    name = "version"
    description = "The version of the project."
    default = 0


class ExtraFiles(InfoElement):

    name = 'extra_files'
    description = """Any extra files needed to build the package.

    This is specified as a dictionary mapping filename to file contents.  The
    filename must be relative to the directory being packaged.
    """
    default = {}

    @classmethod
    def clean(cls, value):
        if isinstance(value, dict):
            return value
        return json.loads(value)


class ExtraFilesFromPaths(ExtraFiles):

    name = 'extra_files_from_paths'
    description = """Any extra files needed to build the package.

    This is specified as a dictionary mapping target filename to
    source filename. The target filename must be relative to the
    directory being packaged. The source filename must be a absolute path
    on disk, and the file will be created from the contents of
    that file. 'extra_files' is preferred to this, but if the files
    may be binary then this alternative is necessary.
    """

class ExtraControlBinaryFields(InfoElement):

    name = 'extra_control_binary_fields'
    description = """Any extra fields for the binary package in debian/control

    If the backend needs to set extra fields in the binary section of
    debian/control it can do so via this element. It should contain
    newline-separated fields, using the colon-separated format, e.g:

        XB-Something: foo
        XB-Something-else: bar

    There should be no trailing newline.
    """


# The following are for 'binary'.

class ApplicationName(InfoElement):

    name = 'application_name'
    description = "The name of an application."


class Categories(InfoElement):

    name = 'categories'
    description = "The categories the application belongs to."


class Executable(InfoElement):

    name = 'executable'
    description = "The path to the executable for an application."


class ExplicitCopyright(InfoElement):

    name = 'explicit_copyright'
    description = 'An explicit copyright statement to override the default.'

    @classmethod
    def clean(cls, value):
        if value is not None:
            return debian_formatted_text(value)


class TagLine(InfoElement):

    name = 'tagline'
    description = "A short line describing the application."


class WorkingDirectory(InfoElement):

    name = 'working_directory'
    description = "The working directory that should be set in the desktop file."


class Icon(InfoElement):

    name = 'icon'
    description = "The name of the icon.  Used in desktop files."


class License(InfoElement):

    name = 'license'
    default = 'unknown'
    description = """The license of the files in the package.

    Note that this will only apply for "simple" cases where there
    is just a single license type. Otherwise it will just write
    a default copyright template that the user needs to fill in.
    """

