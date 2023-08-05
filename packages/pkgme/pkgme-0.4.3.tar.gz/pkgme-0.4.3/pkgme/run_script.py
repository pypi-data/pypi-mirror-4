import errno
import os
import signal
import subprocess
import time

from pkgme.errors import PkgmeError
from pkgme import trace


class ScriptProblem(PkgmeError):

    def __init__(self, script_path, *args):
        super(ScriptProblem, self).__init__(script_path, *args)
        self.script_path = script_path


class ScriptMissing(ScriptProblem):

    def __init__(self, script_path, *args):
        super(ScriptMissing, self).__init__(script_path, *args)

    def __str__(self):
        return "%s not found" % (self.script_path, )


class ScriptPermissionDenied(ScriptProblem):
    """Attempting to run a script led to a permission denied error."""

    def __init__(self, script_path, *args):
        super(ScriptPermissionDenied, self).__init__(script_path, *args)

    def __str__(self):
        return ("permission denied trying to execute %s, is it executable?"
                % (self.script_path, ))


class ScriptFailed(ScriptProblem):

    def __init__(self, command, returncode, output_lines):
        super(ScriptFailed, self).__init__(command, returncode, output_lines)
        self.command = command
        self.returncode = returncode
        self.output_lines = output_lines

    def __str__(self):
        return "%s failed with returncode %s. Output:\n%s" % (
            ' '.join(self.command),
            self.returncode,
            ''.join(' | %s' % (line,)
                    for line in self.output_lines if line))


class ScriptUserError(ScriptFailed):
    """An error from a script meant for end-user consumption."""

    # Scripts exit with this return code to indicate that the error is
    # intended for end users.
    RETURN_CODE = 42

    def __init__(self, command, output_lines):
        super(ScriptUserError, self).__init__(
            command, self.RETURN_CODE, output_lines)

    def __str__(self):
        return ''.join(self.output_lines)


def run_subprocess(cmd, cwd=None, env=None, to_write=None):
    trace.debug("Running %s" % ' '.join(cmd))
    # "Python ignores SIGPIPE on startup, because it prefers to check every
    # write and raise an IOError exception rather than taking the signal."
    #
    # See http://www.chiark.greenend.org.uk/ucgi/~cjwatson/blosxom/2009-07-02-python-sigpipe.html
    start_time = time.time()
    old_sig_pipe = signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    try:
        try:
            proc = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, cwd=cwd, env=env)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise ScriptMissing(cmd[0])
            elif e.errno == errno.EACCES:
                raise ScriptPermissionDenied(cmd[0])
            raise
        output = []
        if to_write:
            proc.stdin.write(to_write)
        proc.stdin.close()
        while True:
            stdout = proc.stdout.readline()
            output.append(stdout)
            if stdout:
                trace.debug('D: %s' % (stdout.rstrip('\n'),))
            else:
                break
        retcode = proc.wait()
        if retcode == 0:
            return output
        elif retcode == ScriptUserError.RETURN_CODE:
            raise ScriptUserError(cmd, output)
        else:
            raise ScriptFailed(cmd, retcode, output)
    finally:
        signal.signal(signal.SIGPIPE, old_sig_pipe)
        trace.log('%r finished in %0.3fs' % (cmd, time.time() - start_time))


def run_script(basepath, script_name, cwd, to_write=None):
    script_path = os.path.join(os.path.abspath(basepath), script_name)
    helperpath = os.path.join(
        os.path.dirname(os.path.dirname(basepath)), 'helpers')
    env = os.environ.copy()
    if os.path.isdir(helperpath):
        if 'PATH' in env:
            env['PATH'] = os.pathsep.join([env['PATH'], helperpath])
        else:
            env['PATH'] = helperpath
    output = run_subprocess([script_path], cwd=cwd, env=env, to_write=to_write)
    return ''.join(output)
