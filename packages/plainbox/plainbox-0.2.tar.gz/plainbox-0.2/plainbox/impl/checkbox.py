# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.

"""
plainbox.impl.checkbox
======================

Internal implementation of plainbox

 * THIS MODULE DOES NOT HAVE STABLE PUBLIC API *
"""

import os

from plainbox.impl import get_plainbox_dir


class CheckBoxNotFound(LookupError):
    """
    Exception used to report that CheckBox cannot be located
    """

    def __repr__(self):
        return "CheckBoxNotFound()"

    def __str__(self):
        return "CheckBox cannot be found"


class CheckBox:
    """
    Helper class for interacting with CheckBox

    PlainBox relies on CheckBox for actual jobs, scripts and library features
    required by the scripts. This class allows one to interact with CheckBox
    without having to bother with knowing how to set up the environment.

    This class also abstracts away the differences between dealing with
    CheckBox that is installed from system packages and CheckBox that is
    available from a checkout directory.
    """

    MODE_DEB_INSTALLED, MODE_SOURCE = range(2)

    # Relative paths to essential CheckBox directories
    # as they exist in a source checkout
    _SRC_SCRIPTS_DIR = "scripts"
    _SRC_JOBS_DIR = "jobs"
    _SRC_DATA_DIR = "data"

    # Absolute paths to essential CheckBox directories
    # as they exist in an installed Debian package
    _DEB_SCRIPTS_DIR = "/usr/lib/checkbox/bin"
    _DEB_JOBS_DIR = "/usr/share/checkbox/jobs"
    _DEB_DATA_DIR = "/usr/share/checkbox/data"
    _DEB_SHARE_DIR = "/usr/share/checkbox"

    def __init__(self, mode=None):
        """
        Initialize checkbox integration.

        Mode, if specified, determines which checkbox to use (either
        MODE_DEB_INSTALLED or MODE_SOURCE). It defaults to auto-detection that
        prefers the source method. It may raise CheckBoxNotFound exception.
        """
        if mode is None:
            if self._source_checkout_exists(self._source_dir):
                mode = self.MODE_SOURCE
            elif self._deb_installation_exists():
                mode = self.MODE_DEB_INSTALLED
            else:
                raise CheckBoxNotFound()
        self._mode = mode

    @property
    def CHECKBOX_SHARE(self):
        """
        Return the required value of CHECKBOX_SHARE environment variable.

        ..note::
            This variable is only required by one script.
            It would be nice to remove this later on.
        """
        if self._mode == self.MODE_DEB_INSTALLED:
            return self._DEB_SHARE_DIR
        elif self._mode == self.MODE_SOURCE:
            return self._source_dir

    @property
    def extra_PYTHONPATH(self):
        """
        Return additional entry for PYTHONPATH, if needed.

        This entry is required for CheckBox scripts to import the correct
        CheckBox python libraries.

        ..note::
            The result may be None
        """
        # NOTE: When CheckBox is installed then all the scripts should not use
        # 'env' to locate the python interpreter (otherwise they might use
        # virtualenv which is not desirable for Debian packages). When we're
        # using CheckBox from source then the source directory (which contains
        # the 'checkbox' package) should be added to PYTHONPATH for all the
        # imports to work.
        if self._mode == self.MODE_DEB_INSTALLED:
            return None
        elif self._mode == self.MODE_SOURCE:
            return self._source_dir

    @property
    def extra_PATH(self):
        """
        Return additional entry for PATH

        This entry is required to lookup CheckBox scripts.
        """
        # NOTE: This is always the script directory. The actual logic for
        # locating it is implemented in the property accessors.
        return self.scripts_dir

    @property
    def jobs_dir(self):
        """
        Return an absolute path of the jobs directory
        """
        if self._mode == self.MODE_DEB_INSTALLED:
            return self._DEB_JOBS_DIR
        else:
            return os.path.join(self._source_dir, self._SRC_JOBS_DIR)

    @property
    def scripts_dir(self):
        """
        Return an absolute path of the scripts directory

        ..note::
            The scripts may not work without setting PYTHONPATH and
            CHECKBOX_SHARE.
        """
        if self._mode == self.MODE_DEB_INSTALLED:
            return self._DEB_SCRIPTS_DIR
        else:
            return os.path.join(self._source_dir, self._SRC_SCRIPTS_DIR)

    @classmethod
    def _source_checkout_exists(cls, location):
        """
        Check if the specified location is a checkbox source directory
        """
        return all((
            os.path.exists(os.path.join(location, dirname))
            for dirname in (
                cls._SRC_SCRIPTS_DIR, cls._SRC_JOBS_DIR, cls._SRC_DATA_DIR)))

    @classmethod
    def _deb_installation_exists(cls):
        """
        Check if a Debian package with checkbox has been installed
        """
        return all((
            os.path.exists(dirname)
            for dirname in (
                cls._DEB_SCRIPTS_DIR, cls._DEB_JOBS_DIR, cls._DEB_DATA_DIR)))

    @property
    def _source_dir(self):
        """
        Return the root directory of the checkbox source checkout

        This only works when plainbox is 'setup.py develop'ed
        and the checkbox submodule has been loaded.
        """
        return os.path.normpath(
            os.path.join(
                get_plainbox_dir(), "..", "checkbox"))
