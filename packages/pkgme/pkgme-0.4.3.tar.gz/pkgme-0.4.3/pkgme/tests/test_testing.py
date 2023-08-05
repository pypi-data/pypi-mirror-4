import os

from testtools import TestCase
from testtools.matchers import (
    DirExists,
    FileContains,
    )

from ..testing import (
    TempdirFixture,
    )


class TestTempdirFixture(TestCase):

    def test_touch(self):
        t = self.useFixture(TempdirFixture())
        t.touch('foo')
        self.assertThat(os.path.join(t.path, 'foo'), FileContains(''))

    def test_touch_with_mode(self):
        t = self.useFixture(TempdirFixture())
        t.touch('foo', 0755)
        self.assertEqual(0755, 0755 & os.stat(os.path.join(t.path, 'foo')).st_mode)

    def test_create_file(self):
        t = self.useFixture(TempdirFixture())
        t.create_file('foo', 'bar')
        self.assertThat(os.path.join(t.path, 'foo'), FileContains('bar'))

    def test_create_deep_file(self):
        t = self.useFixture(TempdirFixture())
        t.create_file(os.path.join('foo', 'bar'), 'content')
        self.assertThat(
            os.path.join(t.path, 'foo', 'bar'), FileContains('content'))


    def test_mkdir(self):
        t = self.useFixture(TempdirFixture())
        t.mkdir('foo')
        self.assertThat(os.path.join(t.path, 'foo'), DirExists())

    def test_mkdir_returns_qualified_path(self):
        t = self.useFixture(TempdirFixture())
        path = t.mkdir('foo')
        self.assertEqual(os.path.join(t.path, 'foo'), path)

    def test_abspath(self):
        t = self.useFixture(TempdirFixture())
        self.assertEqual(
            os.path.abspath(os.path.join(t.path, 'foo')),
            t.abspath('foo'))
