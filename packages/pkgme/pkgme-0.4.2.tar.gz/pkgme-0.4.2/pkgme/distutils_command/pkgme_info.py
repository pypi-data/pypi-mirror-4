from distutils.cmd import Command
import json
import sys
import textwrap


class pkgme_info(Command):
    """distutils command that yields packaging information.

    This command is used to implement the ``all_info`` interface, described in
    the "``pkgme`` backends" documentation.

    Methods beginning with ``get_`` are called automatically by ``run()``
    based on the keys requested by the user.
    """

    user_options = [
        ('pkgmeinfo=', None, "The information to get for pkgme"),
        ('pkgmefile=', None, "The file to write the information to"),
        ]
    boolean_options = []

    def initialize_options(self):
        self.pkgmeinfo = None
        self.pkgmefile = None

    def finalize_options(self):
        if self.pkgmeinfo is None:
            self.pkgmeinfo = []
        else:
            self.pkgmeinfo = self.pkgmeinfo.split(",")

    def run(self):
        info = {}
        for key in self.pkgmeinfo:
            meth = getattr(self, 'get_%s' % (key,), None)
            if meth is not None:
                info[key] = meth()
        def write_info(f):
            f.write(json.dumps(info) + "\n")
        if self.pkgmefile is None:
            write_info(sys.stdout)
        else:
            with open(self.pkgmefile, "w") as f:
                write_info(f)

    def get_package_name(self):
        return self.distribution.get_name()

    def get_description(self):
        description = self.distribution.get_description()
        if self.distribution.get_long_description() != "UNKNOWN":
            description += '\n '.join(
                ['',] + list(
                    textwrap.wrap(
                        self.distribution.get_long_description(), 72)))
        return description

    def get_maintainer(self):
        if (self.distribution.get_maintainer() != 'UNKNOWN' and
            self.distribution.get_maintainer_email() != 'UNKNOWN'):
            return "%s <%s>" % (
                self.distribution.get_maintainer(),
                self.distribution.get_maintainer_email())
        elif (self.distribution.get_author() != 'UNKNOWN' and
              self.distribution.get_author_email() != 'UNKNOWN'):
            return "%s <%s>" % (
                self.distribution.get_author(),
                self.distribution.get_author_email())
        else:
            return "unknown <unknown@unknown>"

    def get_architecture(self):
        if self.distribution.has_ext_modules():
            return "any"
        return "all"

    def get_version(self):
        return self.distribution.get_version()

    def get_buildsystem(self):
        return "python_distutils"

    def get_build_depends(self):
        basics = "python-all, python-setuptools"
        if getattr(self.distribution, "install_requires", None) is not None:
            # FIXME: should avoid depending on this Debian-specific module
            sys.path.insert(1, "/usr/share/python")
            from debpython import pydist

            for pkg in self.distribution.install_requires:
                dep = pydist.guess_dependency(pkg)
                if dep:
                    basics += ", %s" % dep
        return basics

    def get_debhelper_addons(self):
        return "python2"

    def get_depends(self):
        return "${python:Depends}, ${misc:Depends}"
