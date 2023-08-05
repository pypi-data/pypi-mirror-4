import json
from operator import itemgetter
import os
import sys

from pkg_resources import (
    iter_entry_points,
    resource_filename,
    )

from testtools import try_imports

get_platform = try_imports(['sysconfig.get_platform', 'distutils.util.get_platform'])

from pkgme.errors import PkgmeError
from pkgme.project_info import (
    MultipleExternalHelpersInfo,
    SingleExternalHelperInfo,
    )
from pkgme.run_script import (
    run_script,
    ScriptMissing,
    ScriptProblem,
    ScriptUserError,
    )
from pkgme import trace


def get_backend_dir(underunder_file, backend):
    backend_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(underunder_file), os.pardir,
            'backends', backend))
    # When 'python setup.py test' is run with virtualenv, backend_dir will not
    # point to the right place.  It will point into the
    # build/lib.{platform}-{version} directory and that cannot be used as a
    # landmark to find the backends directory.  Assuming we're running the
    # tests from the top of the tree, we do the best we can to find the actual
    # landmark.
    parts = backend_dir.split(os.sep)
    try:
        i = parts.index('build')
        # Stolen from site.py's addbuilddir().
        s = 'lib.%s-%.3s' % (get_platform(), sys.version)
        if hasattr(sys, 'gettotalrefcount'):
            s += '-pydebug'
        if parts[i + 1] == s:
            del parts[i:i+2]
        backend_dir = os.sep.join(parts)
    except (ValueError, IndexError):
        # We're (probably) not in the build environment.
        pass
    return backend_dir


# Where do the backends live?  The environment variable overrides the system
# built-in and discovered development locations.
PKGME_BACKEND_PATHS = os.environ.get('PKGME_BACKEND_PATHS')
if PKGME_BACKEND_PATHS:
    EXTERNAL_BACKEND_PATHS = PKGME_BACKEND_PATHS.split(os.pathsep)
else:
    EXTERNAL_BACKEND_PATHS = [
        resource_filename(__name__, 'backends'),
        os.path.join(sys.prefix, "share", "pkgme", "backends"),
        ]
    for entry_point in iter_entry_points('pkgme.get_backends_path'):
        get_backends_path = entry_point.load()
        backend_location = get_backends_path()
        EXTERNAL_BACKEND_PATHS.append(backend_location)


def get_backend_selector(loader=None, selector_cls=None,
                         allowed_backend_names=None):
    if loader is None:
        loader = get_default_loader()
    backends = loader.load()
    if selector_cls is None:
        selector_cls = get_default_selector
    return selector_cls(
        backends,
        allowed_backend_names=allowed_backend_names)


def get_info_for(path, loader=None, selector_cls=None,
                 allowed_backend_names=None):
    selector = get_backend_selector(
        loader, selector_cls, allowed_backend_names)
    return selector.get_info(path)


def _external_helpers_loader_factory():
    return ExternalHelpersBackendLoader(EXTERNAL_BACKEND_PATHS)


_default_loader_factory = _external_helpers_loader_factory


def get_default_loader():
    global _default_loader_factory
    return _default_loader_factory()


def set_default_loader_factory(loader_factory):
    global _default_loader_factory
    _default_loader_factory = loader_factory


def reset_default_loader_factory():
    global _default_loader_factory
    _default_loader_factory = _external_helpers_loader_factory


def get_default_selector(backends, allowed_backend_names=None):
    return BackendSelector(backends,
            allowed_backend_names=allowed_backend_names)


class Backend(object):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)

    def describe(self):
        return self.name

    def want(self, path):
        """How much this backend wants to be *the* backend.

        :return: (score, reason). 'reason' can be None for older backends.
        """
        raise NotImplementedError(self.want)

    def get_info(self, path):
        raise NotImplementedError(self.get_info)


class WantError(Exception):

    def __init__(self, name, basepath, error, data):
        self.name = name
        self.basepath = basepath
        self.error = error
        self.data = data
        message = (
            "Backend %s (%s) %s from '%s' script: %r"
            % (name, basepath, error, ExternalHelpersBackend.WANT_SCRIPT_NAME,
               data))
        super(WantError, self).__init__(message)


class ExternalHelpersBackend(Backend):

    WANT_SCRIPT_NAME = "want"

    def __init__(self, name, basepath):
        super(ExternalHelpersBackend, self).__init__(name)
        self.basepath = basepath

    def describe(self):
        return "%s (%s)" % (self.name, self.basepath)

    def _parse_want_output(self, output):
        result = output.strip()
        # ints and dicts can be parsed as JSON.
        try:
            result = json.loads(result)
        except ValueError:
            raise WantError(
                self.name, self.basepath, "returned invalid JSON", result)
        try:
            # If it's just an int, return that with no reason.
            return int(result), None
        except TypeError:
            # Do we have a score?  Is 'result' even a dict?
            try:
                score = result['score']
            except KeyError:
                raise WantError(
                    self.name, self.basepath,
                    "did not return a score", result)
            except TypeError:
                raise WantError(
                    self.name, self.basepath,
                    "returned invalid score", result)
            # Is the score an integer?
            try:
                score = int(score)
            except ValueError:
                raise WantError(
                    self.name, self.basepath,
                    "returned non-integer score", result['score'])
            return score, result.get('reason', None)

    def want(self, path):
        try:
            out = run_script(self.basepath, self.WANT_SCRIPT_NAME, path)
        except ScriptUserError:
            raise
        except ScriptMissing:
            raise AssertionError(
                "Backend %s (%s) has no '%s' script"
                % (self.name, self.basepath, self.WANT_SCRIPT_NAME))
        except ScriptProblem, e:
            raise AssertionError(
                "Backend %s (%s) has no usable '%s' script: %s"
                % (self.name, self.basepath, self.WANT_SCRIPT_NAME,
                    str(e)))
        return self._parse_want_output(out)

    def get_info(self, path):
        cls = MultipleExternalHelpersInfo
        if os.path.exists(
            os.path.join(
                self.basepath, SingleExternalHelperInfo.INFO_SCRIPT_NAME)):
            cls = SingleExternalHelperInfo
        return cls(self.basepath, path)


class StaticBackend(Backend):

    def __init__(self, name, score, info, expected_path=None, reason=None):
        """Create a StaticBackend.

        :param name: The name of the backend.
        :param score: A fixed score always returned in response to a 'want'
            call. (But see expected_path).
        :param info: A fixed dict of packaging information always returned in
            response to a 'want' call. (But see expected_path).
        :param expected_path: If provided, then only return 'score' and
            'info' if the backend is being called for this path.
        :param reason: An optional reason for the score we're giving.
        """
        super(StaticBackend, self).__init__(name)
        self.score = score
        self.info = info
        self.expected_path = expected_path
        self.reason = reason

    def want(self, path):
        if self.expected_path is not None:
            assert self.expected_path == path, (
                "Called with cwd of %s, expected %s"
                % (path, self.expected_path))
        return self.score, self.reason

    def get_info(self, path):
        if self.expected_path is not None:
            assert self.expected_path == path, (
                "Called with cwd of %s, expected %s"
                % (path, self.expected_path))
        return self.info


class NoBackend(PkgmeError):
    """Raised when pkgme cannot find any backends."""

    def __init__(self):
        super(NoBackend, self).__init__(
            "No backends found. Looked in %s. Check PKGME_BACKEND_PATHS."
            % (':'.join(EXTERNAL_BACKEND_PATHS)))


class NoEligibleBackend(PkgmeError):
    """Raised when pkgme cannot find an appropriate backend."""

    def __init__(self, path, tried_backends, disallowed_backends=None):
        backend_names = sorted(map(self._describe_result, tried_backends))
        msg = ("No eligible backends for %s. Tried %s"
                % (path, ', '.join(backend_names)))
        if disallowed_backends:
            msg += (". The following backends were disallowed by policy: %s."
                % (', '.join([b.name for b in disallowed_backends])))
        super(NoEligibleBackend, self).__init__(msg)

    @staticmethod
    def _describe_result(result):
        name = result['backend'].name
        reason = result.get('reason', None)
        if reason:
            name = '%s (%s)' % (name, reason)
        return name


def dichotomy(predicate, collection):
    false, true = [], []
    for x in collection:
        if predicate(x):
            true.append(x)
        else:
            false.append(x)
    return false, true


def _query_backend(path, backend):
    score, reason = backend.want(path)
    return {'score': score, 'backend': backend, 'reason': reason}


def _query_backends(path, backends):
    return (_query_backend(path, backend) for backend in backends)


def _is_eligible(backend):
    return backend['score'] > 0


def choose_backend(eligible_backends):
    """Choose the most eligible backend.

    If ``eligible_backends`` is empty, then raises an IndexError.
    """
    bs = sorted(eligible_backends, key=itemgetter('score'), reverse=True)
    return bs[0]['backend']


def query_backends(path, backends, allowed_backend_names=None):
    if not backends:
        raise NoBackend()
    if allowed_backend_names is None:
        disallowed, allowed = [], backends
    else:
        disallowed, allowed = dichotomy(
            lambda b: b.name in allowed_backend_names, backends)
    results = _query_backends(path, allowed)
    ineligible, eligible = dichotomy(_is_eligible, results)
    if not eligible:
        raise NoEligibleBackend(
            path, ineligible, disallowed_backends=disallowed)
    # XXX: Can maybe get rid of this.
    eligible.sort(key=itemgetter('score'), reverse=True)
    return disallowed, ineligible, eligible


class BackendSelector(object):

    def __init__(self, backends, allowed_backend_names=None):
        """Create a BackendSelector.

        A backend selector chooses from a list of backends,
        based on their "want" score for the specified path.

        :param backends: the list of backends to choose from.
        :param allowed_backend_names: a list of backend names
            that are allowable.
        """
        self.backends = backends
        self.allowed_backend_names = allowed_backend_names

    def get_eligible_backends(self, path):
        """Get the backends that could possibly work for ``path``.

        :raise NoBackend: If we can't find any backends at all.
        :raise NoEligibleBackend: If no backend declares itself eligible.
        :return: ``[(score, backend), ...]``.  Will always be sorted with
            the highest score first, and then lexographically by backend name.
        """
        disallowed, ineligible, eligible = query_backends(
            path, self.backends, self.allowed_backend_names)
        return eligible

    def get_info(self, path):
        trace.debug('Finding backend for %s' % (path,))
        eligble = self.get_eligible_backends(path)
        backend = choose_backend(eligble)
        if len(eligble) > 1:
            trace.debug(
                '%s eligble backends. Picked %s' % (len(eligble), backend.name))
        return backend.get_info(path)


class BackendLoader(object):

    def load(self):
        raise NotImplementedError(self.load)


class ExternalHelpersBackendLoader(BackendLoader):

    def __init__(self, paths):
        self.paths = paths

    def load(self):
        backends = []
        names = set()
        for path in self.paths:
            trace.debug("Loading backends from: %s" % (path,))
            path = os.path.abspath(path)
            if not os.path.isdir(path):
                continue
            fnames = os.listdir(path)
            for fname in fnames:
                if fname.startswith("."):
                    continue
                if fname in names:
                    continue
                backend_path = os.path.join(path, fname)
                if not os.path.isdir(backend_path):
                    continue
                trace.debug("  Found backend %s" % (fname,))
                backends.append(
                    ExternalHelpersBackend(fname, backend_path))
                names.add(fname)
        return backends


class StaticLoader(BackendLoader):

    def __init__(self, backends):
        self.backends = backends

    def load(self):
        return self.backends
