import json
import os

from fixtures import (
    EnvironmentVariableFixture,
    MonkeyPatch,
    TempDir,
    )
from testtools import (
    skipUnless,
    TestCase,
    )

from ..info_elements import (
    BuildDepends,
    debian_formatted_text,
    Description,
    Distribution,
    ExtraFiles,
    ExtraFilesFromPaths,
    InfoElement,
    InvalidInfoError,
    Maintainer,
    MissingInfoError,
    PackageName,
    )
from ..project_info import DictInfo


class TestElement(InfoElement):

    name = "test_element"


class RequiredElement(InfoElement):

    name = "required_element"
    required = True
    default = "foo"


class DefaultElement(InfoElement):

    name = "default_element"
    default = "bar"


class TestException(Exception):
    pass


class AlwaysInvalidElement(InfoElement):

    name = "always_invalid_element"

    @classmethod
    def clean(cls, value):
        raise TestException()


class CleaningElement(InfoElement):

    name = "cleaning_element"
    return_value = "some_return_value"

    @classmethod
    def clean(cls, value):
        return cls.return_value


class InfoElementTests(TestCase):

    def test_get_value(self):
        value = self.getUniqueString()
        project_info = DictInfo({TestElement.name: value})
        self.assertEqual(value, TestElement.get_value(project_info))

    def test_get_value_without_value(self):
        self.assertEqual(None, TestElement.get_value(DictInfo({})))

    def test_get_value_with_default(self):
        self.assertEqual("bar", DefaultElement.get_value(DictInfo({})))

    def test_value_required(self):
        e = self.assertRaises(
            MissingInfoError, RequiredElement.get_value, DictInfo({}))
        self.assertEqual(
            "The backend didn't provide a value for 'required_element'",
            str(e))

    def test_clean_can_raise_exception(self):
        self.assertRaises(
            TestException, AlwaysInvalidElement.get_value, DictInfo({}))

    def test_uses_cleaned_value(self):
        original_value = self.getUniqueString()
        self.assertNotEqual(CleaningElement.return_value, original_value)
        project_info = DictInfo({CleaningElement.name: original_value})
        self.assertEqual(
            CleaningElement.return_value, CleaningElement.get_value(project_info))

    def test_default_element_doesnt_clean_value(self):
        original_value = self.getUniqueString()
        project_info = DictInfo({TestElement.name: original_value})
        self.assertEqual(original_value, TestElement.get_value(project_info))


class BuildDependsTestCase(TestCase):

    def test_clean_inserts_debhelper(self):
        value = BuildDepends.clean(None)
        self.assertEqual("debhelper (>= 7)", value)

    def test_clean_adds_debhelper(self):
        value = BuildDepends.clean("python")
        self.assertEqual("python, debhelper (>= 7)", value)

    def test_clean_doesnt_add_debhelper_if_present(self):
        value = BuildDepends.clean("python, debhelper")
        self.assertEqual("python, debhelper", value)

    def test_clean_converts_list(self):
        # BuildDepends can be specified as a list via JSON output from
        # `all_info`.
        value = BuildDepends.clean(["python", "gtk2"])
        self.assertEqual("python, gtk2, debhelper (>= 7)", value)


class ExtraFilesTestCase(TestCase):

    def test_clean_preserves_dict(self):
        in_value = {'foo': 'bar'}
        out_value = ExtraFiles.clean(in_value)
        self.assertEqual(out_value, in_value)

    def test_clean_loads_json(self):
        in_value = {'foo': 'bar'}
        out_value = ExtraFiles.clean(json.dumps(in_value))
        self.assertEqual(out_value, in_value)


class ExtraFilesFromPathsTestCase(TestCase):

    def test_clean_preserves_dict(self):
        in_value = {'foo': 'bar'}
        out_value = ExtraFilesFromPaths.clean(in_value)
        self.assertEqual(out_value, in_value)

    def test_clean_loads_json(self):
        in_value = {'foo': 'bar'}
        out_value = ExtraFilesFromPaths.clean(json.dumps(in_value))
        self.assertEqual(out_value, in_value)


class DistributionTestCase(TestCase):

    @skipUnless(os.path.isfile('/etc/lsb-release'), "No current distro")
    def test_defaults_to_current_distro(self):
        with open('/etc/lsb-release') as fp:
            release_keys = dict(
                line.strip().split('=') for line in fp.readlines())
        self.assertEqual(
            Distribution.get_default(), release_keys['DISTRIB_CODENAME'])

    def test_nonexistent_lsb_release(self):
        tmp_path = self.useFixture(TempDir()).path
        nonexistent = os.path.join(tmp_path, 'nonexistent')
        patch = MonkeyPatch(
            'pkgme.info_elements.Distribution.LSB_RELEASE', nonexistent)
        with patch:
            default_distro = Distribution.get_default()
        self.assertEqual('UNRELEASED', default_distro)


class DebianFormattedTextTests(TestCase):

    # http://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Description

    def test_single_line(self):
        # If the description is just a single line with no line breaks, then
        # that counts as the synopsis and no special formatting is needed.
        description = "single line description"
        cleaned = debian_formatted_text(description)
        self.assertEqual(description, cleaned)

    def test_single_line_trailing_newline(self):
        # If the single line ends with a newline then we remove that newline,
        # as it's not needed for the Description in the template.
        description = "single line description\n"
        cleaned = debian_formatted_text(description)
        self.assertEqual(description.rstrip(), cleaned)

    def test_indented_further_lines(self):
        # If the incoming description is already in the format needed by the
        # control file, then we do nothing to it.
        description = """initial synopsis
 follow-up line
  preformatted text
  more preformatted text
 more information
"""
        cleaned = debian_formatted_text(description)
        self.assertEqual(description.rstrip(), cleaned)

    def test_non_indented_further_lines(self):
        # If the incoming description *looks* like it's in correct Debian
        # format (i.e. has a leading space in the second line), then we assume
        # that they don't know what they are doing and reformat the lines
        # properly.
        bad_description = """\
initial synopsis
 follow-up line
more information
"""
        description = debian_formatted_text(bad_description)
        self.assertEqual("""\
initial synopsis
 follow-up line
 more information""", description)

    def test_bad_literal_description(self):
        # If the incoming description *looks* like it's in correct Debian
        # format (i.e. has a leading space in the second line), but then
        # contains actual blank lines rather than lines with '.', then we
        # raise an error.
        bad_description = """initial synopsis
 follow-up line

 more information
"""
        description = debian_formatted_text(bad_description)
        self.assertEqual("""initial synopsis
 follow-up line
 .
 more information""", description)

    def test_multiple_lines(self):
        # If the description appears to be out of the Debian format and spans
        # multiple lines, then we indent those lines by a single space,
        # treating them as paragraph text that will be word-wrapped.
        description = """initial synopsis
follow-up line
more information
"""
        cleaned = debian_formatted_text(description)
        self.assertEqual("""initial synopsis
 follow-up line
 more information""", cleaned)

    def test_blank_lines(self):
        # If the description appears to be out of the Debian format and
        # contains blank lines, we mark those blank lines with a single '.'.
        description = """initial synopsis
follow-up line

more information

that previous line has spaces in it, but needs to be marked
up as a blank line all the same
"""
        cleaned = debian_formatted_text(description)
        self.assertEqual("""initial synopsis
 follow-up line
 .
 more information
 .
 that previous line has spaces in it, but needs to be marked
 up as a blank line all the same""", cleaned)

    def test_empty_description(self):
        # If the description is empty, then we return an empty description.
        self.assertEqual('', debian_formatted_text(''))
        self.assertEqual('', debian_formatted_text('\n'))
        self.assertEqual('', debian_formatted_text('  '))

    def test_initial_blank_lines(self):
        description = """

initial synopsis
follow-up line
more information
"""
        cleaned = debian_formatted_text(description)
        self.assertEqual("""initial synopsis
 follow-up line
 more information""", cleaned)

    def test_extended_characters_in_descriptions(self):
        # Some people like putting extended characters in their descriptions.
        # Let's see what happens.
        description = (
            u'\u201cPretty \u2018speech\u2019 marks\u201d\u202a \u2013'
            u'what fun!')
        cleaned = debian_formatted_text(description)
        self.assertEqual(description.encode('utf-8'), cleaned)


class DescriptionTestCase(TestCase):

    # http://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Description

    def test_debian_formats_text(self):
        # Description.clean returns the description as Debian-formatted text.
        description = """initial synopsis
follow-up line

more information

that previous line has spaces in it, but needs to be marked
up as a blank line all the same
"""
        cleaned = Description.clean(description)
        self.assertEqual(debian_formatted_text(description), cleaned)


class TestMaintainer(TestCase):

    def test_unspecified(self):
        self.useFixture(EnvironmentVariableFixture('DEBEMAIL', None))
        self.assertEqual(
            Maintainer.default, Maintainer.get_value(DictInfo({})))

    def test_from_environment_variable(self):
        debemail = 'Dude <dude@example.com>'
        self.useFixture(EnvironmentVariableFixture('DEBEMAIL', debemail))
        self.assertEqual(debemail, Maintainer.get_value(DictInfo({})))

    def test_clean_full(self):
        # A full name <email> is untouched by clean
        debemail = 'Dude <dude@example.com>'
        self.assertEqual(debemail, Maintainer.clean(debemail))

    def test_clean_email(self):
        # Just an email is duplicated
        debemail = 'dude@example.com'
        self.assertEqual("%s <%s>" % (debemail, debemail),
                Maintainer.clean(debemail))

    def test_clean_email_in_brackets(self):
        # An email in brackets is duplicated minus the quotes
        debemail = 'dude@example.com'
        self.assertEqual("%s <%s>" % (debemail, debemail),
                Maintainer.clean("<%s>" % debemail))

    def test_clean_name(self):
        # A name is given an example email address
        debemail = 'Dude'
        self.assertEqual("%s <person@example.com>" % (debemail,),
                Maintainer.clean(debemail))

    def test_name_in_brackets(self):
        # A name in brackets is given an example email address
        debemail = 'Dude'
        self.assertEqual("%s <person@example.com>" % (debemail,),
                Maintainer.clean("<%s>" % debemail))


class TestPackageName(TestCase):

    def test_valid(self):
        cleaned = PackageName.clean('foo')
        self.assertEqual('foo', cleaned)

    def test_capitals(self):
        cleaned = PackageName.clean('Foo')
        self.assertEqual('foo', cleaned)

    def test_too_short(self):
        e = self.assertRaises(InvalidInfoError, PackageName.clean, 'f')
        self.assertEqual(
            "Package name must be at least two characters long: 'f'", str(e))

    def test_invalid_characters(self):
        cleaned = PackageName.clean('foo&ba@r')
        self.assertEqual('foobar', cleaned)

    def test_too_short_after_stripping(self):
        e = self.assertRaises(InvalidInfoError, PackageName.clean, 'f&&&')
        self.assertEqual(
            "Package name must be at least two characters long: 'f&&&'",
            str(e))
        e = self.assertRaises(InvalidInfoError, PackageName.clean, '+++f')
        self.assertEqual(
            "Package name must be at least two characters long: '+++f'",
            str(e))

    def test_invalid_start_character(self):
        self.assertEqual('foobar', PackageName.clean('+foobar'))
        self.assertEqual('foobar', PackageName.clean('-foobar'))
        self.assertEqual('foobar', PackageName.clean('.foobar'))

