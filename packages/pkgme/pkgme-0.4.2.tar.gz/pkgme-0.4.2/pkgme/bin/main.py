#!/usr/bin/python

import argparse
import json
import os
import sys

from pkgme import __version__
from ..api import get_all_info
from pkgme.api import (
    build_package,
    get_eligible_backends,
    load_backends,
    packaging_info_as_data,
    write_packaging_info,
    )
from pkgme.backend import (
    EXTERNAL_BACKEND_PATHS,
    get_default_loader,
    )
from pkgme.info_elements import Distribution
from pkgme.project_info import override_info
from pkgme.upload import (
    InvalidPPAName,
    parse_ppa_name,
    )
from pkgme.errors import PkgmeError
from pkgme import trace


def make_arg_parser():
    def ppa_type(ppa_name):
        try:
            parse_ppa_name(ppa_name)
        except InvalidPPAName, e:
            raise argparse.ArgumentTypeError(str(e))
        return ppa_name
    parser = argparse.ArgumentParser(
        description='pkgme - A Debian packaging generation framework.')
    parser.add_argument(
        '-v', '--version', action='store_true',
        help='Print this version string and exit')
    parser.add_argument('-D', '--debug', action='store_true')
    parser.add_argument('--dump', action='store_true')
    parser.add_argument('--which-backends', action='store_true')
    parser.add_argument(
        '-d', '--distro',
        help="The distribution to upload to. e.g. 'oneiric' or 'unstable'.")
    parser.add_argument(
        'ppa', nargs='?', metavar='PPA', type=ppa_type,
        help='A PPA to upload to. e.g. ppa:user/ppa-name')
    parser.add_argument('--nosign', action='store_true', default=None,
                        help="Do not sign resulting source packages.")
    parser.add_argument('--nobuild', action='store_true', default=None,
                        help="Do not build a source packages.")
    return parser


def get_version_info(debug=False):
    version = 'pkgme %s' % (__version__,)
    if debug:
        ls = [version, '']
        ls.append('Backend paths: %s' % ', '.join(map(repr, EXTERNAL_BACKEND_PATHS)))
        ls.append("Available backends:")
        loader = get_default_loader()
        backends = loader.load()
        for backend in backends:
            ls.append(" %s" % backend.describe())
        version = '\n'.join(ls)
    return version


def _dump_decision(decision, stream):
    json.dump(
        packaging_info_as_data(decision), stream, sort_keys=True, indent=2)


def _format_eligible_backends(backends):
    return ', '.join(
        '%s (%s)' % (r['backend'].name, r['score']) for r in backends)


def main(argv=None, target_dir=None, interactive=True):
    if argv is None:
        argv = sys.argv[1:]
    parser = make_arg_parser()
    options = parser.parse_args(args=argv)
    if options.version:
        print get_version_info(options.debug)
        return 0
    if options.debug:
        trace.set_debug()
    if target_dir is None:
        target_dir = os.getcwd()
    overrides = None
    if options.distro:
        overrides = {Distribution: options.distro}
    try:
        backends = load_backends()
        if options.which_backends:
            eligible = get_eligible_backends(target_dir, backends)
            print _format_eligible_backends(eligible)
        else:
            decision = get_all_info(target_dir, backends)
            if options.dump:
                _dump_decision(decision, sys.stdout)
            else:
                trace.debug("Writing packaging for %s" % (target_dir,))
                info = override_info(decision['info'], overrides)
                write_packaging_info(target_dir, info)
                trace.debug("Wrote packaging for %s" % (target_dir,))
                if not options.nobuild:
                    if options.nosign is None:
                        sign = None
                    else:
                        sign = not options.nosign
                    build_package(
                        target_dir, interactive=interactive, ppa=options.ppa,
                        sign=sign)
    except PkgmeError, e:
        if options.debug:
            raise
        else:
            sys.stderr.write("ERROR: %s\n" % (e,))
            return 3
    return 0


if __name__ == '__main__':
    sys.exit(main())
