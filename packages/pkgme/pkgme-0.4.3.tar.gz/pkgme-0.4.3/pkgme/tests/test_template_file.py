from testtools import TestCase

from ..template_file import TemplateFile


class TemplateFileTests(TestCase):

    def test_render(self):
        t = TemplateFile("test_dummy")
        self.assertIn("TEST DUMMY", t.render(dict(var="foo")))

    def test_render_passes_data(self):
        t = TemplateFile("test_dummy")
        self.assertIn("foo", t.render(dict(var="foo")))
