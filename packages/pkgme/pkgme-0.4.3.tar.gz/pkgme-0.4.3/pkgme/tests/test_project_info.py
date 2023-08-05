import json
import sys

from fixtures import TempDir
from testtools import TestCase
from treeshape import (
    CONTENT,
    FileTree,
    PERMISSIONS,
    )

from ..project_info import (
    DictInfo,
    FallbackInfo,
    MultipleExternalHelpersInfo,
    SingleExternalHelperInfo,
    )
from ..run_script import (
    ScriptFailed,
    ScriptPermissionDenied,
    )


class DictInfoTests(TestCase):

    def test_get_one(self):
        key = self.getUniqueString()
        value = self.getUniqueString()
        info = DictInfo({key: value})
        self.assertEqual({key: value}, info.get_all([key]))

    def test_get_multiple(self):
        key1 = self.getUniqueString()
        value1 = self.getUniqueString()
        key2 = self.getUniqueString()
        value2 = self.getUniqueString()
        info = DictInfo({key1: value1, key2: value2})
        self.assertEqual(
            {key1: value1, key2: value2}, info.get_all([key1, key2]))

    def test_get_missing(self):
        key = self.getUniqueString()
        value = self.getUniqueString()
        info = DictInfo({key: value})
        self.assertEqual({}, info.get_all(self.getUniqueString()))

    def test_get_one_missing(self):
        key1 = self.getUniqueString()
        value1 = self.getUniqueString()
        key2 = self.getUniqueString()
        info = DictInfo({key1: value1})
        self.assertEqual(
            {key1: value1}, info.get_all([key1, key2]))


class FallbackInfoTests(TestCase):

    def test_uses_first(self):
        key = self.getUniqueString()
        value = self.getUniqueString()
        info1 = DictInfo({key: value})
        info2 = DictInfo({})
        info = FallbackInfo(info1, info2)
        self.assertEqual({key: value}, info.get_all([key]))

    def test_falls_back_to_second(self):
        key = self.getUniqueString()
        value = self.getUniqueString()
        info1 = DictInfo({})
        info2 = DictInfo({key: value})
        info = FallbackInfo(info1, info2)
        self.assertEqual({key: value}, info.get_all([key]))

    def test_uses_first_when_second_present(self):
        key = self.getUniqueString()
        value1 = self.getUniqueString()
        value2 = self.getUniqueString()
        info1 = DictInfo({key: value1})
        info2 = DictInfo({key: value2})
        info = FallbackInfo(info1, info2)
        self.assertEqual({key: value1}, info.get_all([key]))


class MultipleExternalHelpersInfoTests(TestCase):

    def make_script(self, name, contents, permission=0700):
        return self.useFixture(
            FileTree({name: {CONTENT: contents,
                             PERMISSIONS: permission}})).path

    def test_missing_helper(self):
        tempdir = self.useFixture(TempDir()).path
        info = MultipleExternalHelpersInfo(tempdir, tempdir)
        key = self.getUniqueString()
        self.assertEqual({key: None}, info.get_all([key]))

    def test_uses_output(self):
        script_name = self.getUniqueString()
        value = self.getUniqueString()
        script = "#!/bin/sh\necho %s\n" % value
        tempdir = self.make_script(script_name, script)
        info = MultipleExternalHelpersInfo(tempdir, tempdir)
        self.assertEqual({script_name: value}, info.get_all([script_name]))

    def test_script_error(self):
        script_name = self.getUniqueString()
        script = "#!/bin/sh\nexit 1\n"
        tempdir = self.make_script(script_name, script)
        info = MultipleExternalHelpersInfo(tempdir, tempdir)
        self.assertRaises(
            ScriptFailed, info.get_all, [script_name])

    def test_script_permission_denied(self):
        """Check the exception raised when the info script isn't executable."""
        script_name = self.getUniqueString()
        script = "#!/bin/sh\nexit 0\n"
        tempdir = self.make_script(script_name, script, 0644)
        info = MultipleExternalHelpersInfo(tempdir, tempdir)
        self.assertRaises(
            ScriptPermissionDenied, info.get_all, [script_name])

    def test_correct_working_directory(self):
        cwd_tempdir = self.useFixture(TempDir()).path
        script_name = self.getUniqueString()
        script = "#!%s\nimport os\nprint os.getcwd()\n" % sys.executable
        script_tempdir = self.make_script(script_name, script)
        info = MultipleExternalHelpersInfo(script_tempdir, cwd_tempdir)
        self.assertEqual(
            {script_name: cwd_tempdir}, info.get_all([script_name]))


class SingleExternalHelperInfoTests(TestCase):

    def make_script(self, contents, permission=0700):
        name = SingleExternalHelperInfo.INFO_SCRIPT_NAME
        return self.useFixture(
            FileTree({name: {CONTENT: contents,
                             PERMISSIONS: permission}}))

    def test_uses_output(self):
        element_name = self.getUniqueString()
        value = self.getUniqueString()
        script = '#!%s\nimport json\nprint json.dumps(%s)\n' % (
            sys.executable, json.dumps({element_name: value}))
        tempdir = self.make_script(script).path
        info = SingleExternalHelperInfo(tempdir, tempdir)
        self.assertEqual({element_name: value}, info.get_all([element_name]))

    def test_when_script_gives_invalid_json_output(self):
        """Test when the script doesn't produce valid JSON.

        As this is a problem with the backend we expect an AssertionError
        with an intelligible message.
        """
        script = '#!%s\nprint "}Nonsense"' % (sys.executable, )
        tempdir = self.make_script(script)
        info = SingleExternalHelperInfo(tempdir.path, tempdir.path)
        e = self.assertRaises(AssertionError, info.get_all, [])
        self.assertEquals(
            "%s didn't return valid JSON: '}Nonsense\\n'" % (
                tempdir.join(SingleExternalHelperInfo.INFO_SCRIPT_NAME),),
            str(e))

    def test_passes_input(self):
        element_name = self.getUniqueString()
        value = self.getUniqueString()
        script = """#!%(python)s
import json
import sys

raw_input = sys.stdin.read()
input = json.loads(raw_input)
if input != ["%(element)s"]:
    print json.dumps({"%(element)s": "Did not pass correct input: %%s" %% raw_input})
else:
    print json.dumps({"%(element)s": "%(value)s"})
""" % {'python': sys.executable, 'element': element_name, 'value': value}
        tempdir = self.make_script(script).path
        info = SingleExternalHelperInfo(tempdir, tempdir)
        self.assertEqual({element_name: value}, info.get_all([element_name]))

    def test_correct_working_directory(self):
        cwd_tempdir = self.useFixture(TempDir())
        element_name = self.getUniqueString()
        script = """#!%s
import os
import json
print json.dumps({"%s": os.getcwd()})
""" % (sys.executable, element_name)
        script_tempdir = self.make_script(script).path
        info = SingleExternalHelperInfo(script_tempdir, cwd_tempdir.path)
        self.assertEqual(
            {element_name: cwd_tempdir.path}, info.get_all([element_name]))
