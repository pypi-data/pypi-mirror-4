import json
import os
from pprint import pformat

from pkgme.run_script import run_script, ScriptMissing
from pkgme import trace


class ProjectInfo(object):

    def get_all(self, keys):
        raise NotImplementedError(self.get_all)


class DictInfo(ProjectInfo):

    def __init__(self, info):
        self.info = info

    def get_all(self, keys):
        values = {}
        for key in keys:
            if key in self.info:
                values[key] = self.info[key]
        return values


def to_info(d):
    """Make a ``DictInfo`` out of an InfoElement -> value dict."""
    return DictInfo(dict((k.name, d[k]) for k in d))


def override_info(info, overrides):
    if not overrides:
        return info
    return FallbackInfo(to_info(overrides), info)


class FallbackInfo(ProjectInfo):
    """Combine many ProjectInfos into one, falling back to later infos.

    Can be used to mask values in a ProjectInfo.
    e.g. FallbackInfo(DictInfo(masking_dict), get_info_for(path))
    """

    def __init__(self, *infos):
        self.infos = list(infos)

    def get_all(self, keys):
        values = {}
        keys = set(keys)
        for info in self.infos:
            found_values = info.get_all(list(keys))
            values.update(found_values)
            keys -= set(found_values.keys())
            if not keys:
                break
        return values


class _ExternalHelpersInfo(ProjectInfo):

    def __init__(self, basepath, cwd):
        self.basepath = basepath
        self.cwd = cwd


class SingleExternalHelperInfo(_ExternalHelpersInfo):

    INFO_SCRIPT_NAME = "all_info"

    def get_all(self, keys):
        out = run_script(
            self.basepath, self.INFO_SCRIPT_NAME, self.cwd,
            to_write=json.dumps(keys))
        try:
            ret = json.loads(out)
        except ValueError:
            raise AssertionError("%s didn't return valid JSON: %r"
                    % (os.path.join(self.basepath, self.INFO_SCRIPT_NAME),
                        out))
        trace.debug('%s returned %s' % (self.INFO_SCRIPT_NAME, pformat(ret)))
        return ret


class MultipleExternalHelpersInfo(_ExternalHelpersInfo):

    def _get(self, key):
        try:
            out = run_script(self.basepath, key, self.cwd)
        except ScriptMissing:
            ret = None
        else:
            ret = out.rstrip("\n")
        trace.debug('%s returned %s' % (key, pformat(ret)))
        return ret

    def get_all(self, keys):
        values = {}
        for key in keys:
            values[key] = self._get(key)
        return values
