# pkgme - A Debian packaging framework
#
# Copyright (C) 2010-2012 Canonical Ltd.
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

"""Package symbols."""

from __future__ import absolute_import, unicode_literals

__all__ = [
    '__version__',
    'write_packaging',
    ]

__version__ = '0.4.2'


def write_packaging(path, distribution=None, allowed_backend_names=None):
    """DEPRECATED - Use ``pkgme.api.write_packaging_info`` instead."""
    # Do these imports in the function to reduce the side-effects of importing
    # pkgme.  This avoids the need for setup.py of the tool being packaged
    # from having to find all the imported dependencies when running the
    # extension pkgme_info setup.py command.
    from .api import (
        load_backends,
        get_all_info,
        write_packaging_info,
        )
    from .info_elements import Distribution
    from .project_info import override_info
    backends = load_backends()
    decision = get_all_info(path, backends, allowed_backend_names)
    info = decision['info']
    if distribution:
        info = override_info(info, {Distribution: distribution})
    return write_packaging_info(path, info)
