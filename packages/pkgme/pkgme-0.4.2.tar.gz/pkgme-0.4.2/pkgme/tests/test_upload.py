from testtools import TestCase

from ..upload import (
    CannotUpload,
    InvalidPPAName,
    NoSuchPerson,
    NoSuchPPA,
    parse_ppa_name,
    )


class NamedThing(object):

    def __init__(self, name):
        self.name = name


class TestPPAChecking(TestCase):

    def test_parse_ppa_name(self):
        self.assertEqual(('foo', 'bar'), parse_ppa_name('ppa:foo/bar'))

    def test_parse_invalid_ppa_name(self):
        self.assertRaises(InvalidPPAName, parse_ppa_name, 'oscar')
        self.assertRaises(InvalidPPAName, parse_ppa_name, '11:45pm')
        self.assertRaises(InvalidPPAName, parse_ppa_name, 'whatever:foo/bar')
        self.assertRaises(InvalidPPAName, parse_ppa_name, 'ppa:foo/bar/baz')
        self.assertRaises(InvalidPPAName, parse_ppa_name, 'ppa:foo/bar:baz')

    def test_invalid_ppa_name(self):
        e = InvalidPPAName('oscar')
        self.assertEqual(
            'Invalid PPA name: oscar. Expected "ppa:<person>/<archive>".',
            str(e))

    def test_no_such_person(self):
        e = NoSuchPerson('foo')
        self.assertEqual('No such person: foo', str(e))

    def test_no_such_archive(self):
        e = NoSuchPPA('foo')
        self.assertEqual('No such PPA: foo', str(e))

    def test_cannot_upload(self):
        e = CannotUpload(NamedThing('foo'), 'ppa:bar/baz', NamedThing('bar'))
        self.assertEqual(
            'foo cannot upload to ppa:bar/baz. Must be a member of ~bar',
            str(e))
