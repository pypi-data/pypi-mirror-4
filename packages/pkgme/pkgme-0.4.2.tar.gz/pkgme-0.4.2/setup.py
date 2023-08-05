# pkgme - A Debian packaging framework
#
# Copyright (C) 2010 Canonical Ltd.
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

import os

import distribute_setup
# What is specified here is the minimum version, and the version
# that will be installed if there isn't one already. We specify
# it so that we can update distribute_setup without it implying
# that we require the latest version, which can cause unnecessary
# updating, and can fail if there is a version conflict.
# If we do require a higher minimum version then update it here
# and ensure that distribute_setup is at least as new as that
# version.
distribute_setup.use_setuptools(version='0.6.10')

from setup_helpers import (
    description, find_doctests, get_version, long_description, require_python)
from setuptools import setup, find_packages


require_python(0x20600f0)
__version__ = get_version('pkgme/__init__.py')

def get_data_files():
    source_dir = os.path.dirname(__file__)
    package_dir = os.path.join(source_dir, "pkgme")
    data_files = []
    base_data_install_dir = os.path.join('share', 'pkgme')

    def install_data_tree(package_subdir):
        source_dir = os.path.join(package_dir, package_subdir)
        target_base_dir = os.path.join(base_data_install_dir, package_subdir)
        for dirpath, dirname, filenames in os.walk(source_dir):
            paths = [os.path.join(dirpath, fn) for fn in filenames]
            target_path = target_base_dir
            relpath = os.path.relpath(dirpath, source_dir)
            if relpath != ".":
                target_path = os.path.join(target_path, relpath)
            data_files.append((target_path, paths))

    install_data_tree("helpers")
    install_data_tree("backends")
    return data_files


setup(
    name='pkgme',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    maintainer='pkgme developers',
    maintainer_email='pkgme-devs@lists.launchpad.net',
    description=description('README.txt'),
    long_description=long_description(
        'README.txt',
        'NEWS.txt',
        ),
    license='GPLv3',
    url='http://launchpad.net/pkgme',
    test_suite='pkgme.tests',
    install_requires = [
        'Cheetah',
        'python_debian',
        'fixtures',
        'launchpadlib',
        'Markdown', # "Required" by Cheetah, but only a suggests in the packaging.
        'testtools',
        ],
    entry_points = {
        'console_scripts': ['pkgme=pkgme.bin.main:main'],
        },
    data_files = get_data_files(),
    # Auto-conversion to Python 3.
    use_2to3=True,
    convert_2to3_doctests=find_doctests(),
    )
