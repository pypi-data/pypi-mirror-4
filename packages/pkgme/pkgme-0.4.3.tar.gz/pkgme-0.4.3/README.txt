=====
pkgme
=====

The ``pkgme`` program is a framework for generating Debian packaging artifacts
from information gleaned from inspecting the code.  The framework takes care
of the common tasks, and knows about packaging in general.  It is extensible
so that programming language-specific conventions and rules can be supported.


Project information
===================

``pkgme`` development is `hosted on Launchpad`_.  Please see the project page
for downloads, bug reports, and accessing the latest code (available in the
Bazaar_ version control system).  You can also subscribe to the `pkgme mailing
list`_ for discussions on using and extending ``pkgme``.  The archives_ are
also available on-line.


.. _`hosted on Launchpad`: http://launchpad.net/pkgme
.. _Bazaar: http://bazaar.canonical.com
.. _`pkgme mailing list`: https://launchpad.net/~pkgme-devs
.. _archives: https://lists.launchpad.net/pkgme-devs/


Dependencies
============

In addition to the various Python modules documented in ``setup.py``,
``pkgme`` depends on ``devscripts`` and ``debhelper``.


Developers
==========

To get a development environment set up (using ``buildout``) run::

   $ make bootstrap

You can then run the tests with

   $ make check

The bootstrap will fail if you have a system-wide install of buildout that
is the same version as the one in use by this project. (You will see
``DistributionNotFound: zc.buildout==<version>``). If you encounter
that then you can either remove the site-wide install, or use a virtualenv
to run the bootstrap step.

You can get a shell to try code interactively by running ``./bin/py``.

Buildout uses two directories as caches that can be shared between branches.
The first is the ``download-cache`` directory. This contains all of the
distributions of the Python dependencies. You can get this from
``lp:ca-download-cache``, but the Makefile will grab it for you.

The other directory is the ``eggs`` directory that holds built versions
of the dependencies.

The default for both of these is to symlink them from the parent directory,
but if you wish to put them somewhere else you can set the locations with
the ``CA_DOWNLOAD_CACHE_DIR`` and ``CA_EGGS_DIR`` environment variables.


If you want to override the default location of the backends, set the
environment variable ``$PKGME_BACKEND_PATHS``.  This is a colon-separated list
of directories, for example:

    % export PKGME_BACKEND_PATHS=/pkgme/foo-backends:/pkgme/bar-backends
    % cd my-about-to-be-packaged-code
    % ~/path/to/branch/bin/pkgme


Building the documentation
--------------------------

If you have the Sphinx toolchain installed (on Debian/Ubuntu, the
python-sphinx package), you can build the documentation like so::

    % make html

You'll need to be in your virtualenv, and you should have installed ``pkgme``
in that virtualenv before trying to build the documentation.


.. _virtualenv: http://virtualenv.openplans.org/


Table of Contents
=================

.. toctree::
    :glob:

    *
..
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


