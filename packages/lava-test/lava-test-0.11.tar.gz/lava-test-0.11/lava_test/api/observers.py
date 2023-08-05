# Copyright (c) 2010, 2011 Linaro
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
:mod:`lava_test.api.observers` -- Interface classes for observer classes
========================================================================

.. module: lava_test.api.observers
    :synopsis: Interface classes for observer classes
"""

from abc import abstractmethod

from lava_test.api import _Interface


class IShellCommandObserver(_Interface):
    """
    Shell command runner observer class.

    Allows the caller to observe shell commands that occur during some
    operation. It is used by the command line UI.

        .. versionadded:: 0.2
    """

    @abstractmethod
    def about_to_run_shell_command(self, cmd):
        """
        Method called when a shell command is about to be invoked by the
        observed object.

        .. versionadded:: 0.2
        """

    @abstractmethod
    def did_run_shell_command(self, cmd, returncode):
        """
        Method called when a shell command has been invoked by the observed
        object.

        .. versionadded:: 0.2
        """

    @abstractmethod
    def display_subprocess_output(self, stream_name, line):
        """
        Method called for each line of stdout/stderr as obtained from a
        subprocess.

        .. versionadded:: 0.2
        """


class ITestInstallerObserver(IShellCommandObserver):
    """
    Test installer observer class.

    Allows the caller to observe interesting actions that occur during
    installation process. It is used by the command line UI.

        .. versionadded:: 0.2
    """

    @abstractmethod
    def about_to_install_packages(self, package_list):
        """
        Method called when a list of packages is about to be installed by the
        installer

        .. versionadded:: 0.2
        """

    @abstractmethod
    def did_install_packages(self, package_list):
        """
        Method called when a package has been installed by the installer

        .. versionadded:: 0.2
        """

    @abstractmethod
    def about_to_download_file(self, url):
        """
        Method called when a file is about to be downloaded

        .. versionadded:: 0.2
        """

    @abstractmethod
    def did_download_file(self, url):
        """
        Method called when a file has been downloaded

        .. versionadded:: 0.2
        """


class ITestRunnerObserver(IShellCommandObserver):
    """
    Test runner observer class.

    Allows the caller to observe interesting actions that occur during testing
    process. It is used by the command line UI.

        .. versionadded:: 0.2
    """
