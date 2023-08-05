# pkgme - A Debian packaging framework
#
# Copyright (C) 2010 Canonical Lt.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Python API for using pkgme."""

from __future__ import absolute_import, unicode_literals

__all__ = [
    'build_package',
    'get_all_info',
    'get_eligible_backends',
    'load_backends',
    'packaging_info_as_data',
    'write_packaging_info',
    ]

import time

from . import trace
from .backend import (
    choose_backend,
    get_default_loader,
    query_backends,
    )
from .debuild import build_source_package
from .package_files import default_package_file_group
from .upload import upload
from .write import Writer


def build_package(target_dir, interactive, ppa=None, sign=None):
    """Build a Debian source package in ``target_dir``.

    :param target_dir: A directory containing a thing to be packaged, along
        with a valid debian/ directory.
    :param ppa: If specified, a PPA location to upload the source package to.
    """
    trace.debug("Building source package for %s" % (target_dir,))
    if sign is not None:
        changes_file = build_source_package(target_dir, sign=sign)
    else:
        changes_file = build_source_package(target_dir, sign=interactive)
    trace.debug("Built source package for %s" % (target_dir,))
    if ppa:
        trace.debug('Uploading to PPA: %s => %s' % (changes_file, ppa))
        upload(changes_file, ppa)
        trace.debug('Uploaded to PPA: %s => %s' % (changes_file, ppa))


def load_backends():
    """Load backends in the default way.

    :return: A list of backends.
    """
    return get_default_loader().load()


def get_eligible_backends(target_dir, backends):
    """Return eligible backends for ``target_dir``.

    Eligible backends are those that return a non-zero score.  Sort order is
    not guaranteed.
    """
    return query_backends(target_dir, backends)[2]


def get_all_info(path, backends, allowed_backend_names=None):
    """Get all possible packaging information about ``path``.

    NOTE: Do not confuse this with ``pkgme.bin.main.get_all_info`` which is a
    deprecated function that returns nearly exactly the same information but
    as plain Python data structures.

    :param path: A path on disk containing a thing to be packaged.
    :param backends: A list of backends to query.  You can get such a list
        using ``load_backends()``.
    :param allowed_backend_names: A whitelist of allowed backend names.  If
        not provided, all backends are allowed.
    :return: A dict with the following keys:
        disallowed:: a list of backends found but forbidden
        ineligible:: a list of backends that returned a score of 0
        eligible::   a list of backends that returned a non-zero score
        backend::    the backend with the best score
        info::       the ``ProjectInfo`` returned by that backend

        ``eligible`` and ``ineligible`` each are a list of dicts with keys
        ``backend``, ``score`` and ``reason``.
    """
    disallowed, ineligible, eligible = query_backends(
        path, backends, allowed_backend_names)
    backend = choose_backend(eligible)
    info = backend.get_info(path)
    return dict(
        disallowed=disallowed,
        ineligible=ineligible,
        eligible=eligible,
        backend=backend,
        info=info)


def packaging_info_as_data(decision):
    """Convert the result of ``get_all_info`` to plain dict.

    Takes the rich objects in ``decision`` and converts them to Python data
    structures that can be serialized as JSON.
    """

    def get_all_keys():
        # XXX: This ignores ExtraFiles and ExtraFilesFromPaths because they
        # aren't in get_elements().
        elements = default_package_file_group.get_elements()
        return [element.name for element in elements]

    def encode_backend(result):
        result.update({'backend': result['backend'].name})
        return result

    data = decision['info'].get_all(get_all_keys())
    data[u'selected_backend'] = decision['backend'].name
    data[u'eligible_backends'] = map(encode_backend, decision['eligible'])
    return data


def write_packaging_info(path, info):
    """Write packaging information for 'path'.

    :param path: Path to write the packaging information to.
    :param info: A ``ProjectInfo`` containing everything we need to package it.
    """
    start_time = time.time()
    files = default_package_file_group.get_files(info)
    Writer().write(files, path)
    trace.log("Wrote packaging files in %0.3fs" % (time.time() - start_time,))
