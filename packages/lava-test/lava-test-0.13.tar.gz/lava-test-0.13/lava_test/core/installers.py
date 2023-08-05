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

import hashlib
import os
import subprocess

from lava_test.api.delegates import ITestInstaller
from lava_test.extcmd import ExternalCommandWithDelegate
from lava_test.utils import changed_directory, geturl


class TestInstaller(ITestInstaller):
    """
    Base class for defining an installer object.

    This class can be used as-is for simple installers, or extended
    for more advanced functionality.

    :ivar steps:
        List of steps to be executed in a shell

    :ivar deps:
        List of Debian or Ubuntu packages to apt-get install before running the
        steps.

    :ivar url:
        Location from which the test suite should be downloaded.

    :ivar md5:
        The md5sum to check the integrety of the download

    :ivar git_repos:
        A list of git urls to clone for the test definition. These will be
        cloned befre the install steps are executed for the test definition.
        The repo information will then be included in the bundle's source data

    :ivar bzr_repos:
        A list of git urls to clone for the test definition. These will be
        cloned befre the install steps are executed for the test definition.
        The repo information will then be included in the bundle's source data
    """
    def __init__(self, steps=None, deps=None, url=None, md5=None,
            git_repos=None, bzr_repos=None, **kwargs):
        self.steps = steps or []
        self.deps = deps or []
        self.url = url
        self.md5 = md5
        self.git_repos = git_repos
        self.bzr_repos = bzr_repos

    def __repr__(self):
        return "<%s steps=%r deps=%r url=%r md5=%r>" % (
            self.__class__.__name__,
            self.steps, self.deps, self.url, self.md5)

    def _run_shell_cmd(self, cmd, observer):
        if observer:
            observer.about_to_run_shell_command(cmd)
        extcmd = ExternalCommandWithDelegate(observer)
        returncode = extcmd.check_call(cmd, shell=True)
        if observer:
            observer.did_run_shell_command(cmd, returncode)

    def _installdeps(self, observer):
        if self.deps:
            if observer:
                observer.about_to_install_packages(self.deps)
            # XXX: Possible point of target-specific package installation
            cmd = "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --force-yes " + " ".join(self.deps)
            self._run_shell_cmd(cmd, observer)
            if observer:
                observer.did_install_packages(self.deps)

    def _download(self, observer):
        """
        Download the file specified by the url and check the md5.

        Returns the path and filename if successful, otherwise return None
        """
        if not self.url:
            return
        if observer:
            observer.about_to_download_file(self.url)
        filename = geturl(self.url)
        # If the file does not exist, then the download was not
        # successful
        if not os.path.exists(filename):
            raise RuntimeError(
                "Failed to download %r" % self.url)
        if observer:
            observer.did_download_file(self.url)
        if self.md5:
            checkmd5 = hashlib.md5()
            with open(filename, 'rb') as fd:
                data = fd.read(0x10000)
                while data:
                    checkmd5.update(data)
                    data = fd.read(0x10000)
            if checkmd5.hexdigest() != self.md5:
                raise RuntimeError(
                    "md5sum mismatch of file %r, got %s expected %s" % (
                        filename, checkmd5.hexdigest(), self.md5))
        return filename

    def _git_local(self, repo):
        """
        convert git url into the local name, it git://foo.com/blah.git to blah
        """
        return os.path.splitext(os.path.basename(repo))[0]

    def _git_clone(self, observer):
        if not self.git_repos:
            return

        for repo in self.git_repos:
            if observer:
                observer.about_to_download_file(repo)

            self._run_shell_cmd("git clone %s" % repo, observer)

            if not os.path.exists(self._git_local(repo)):
                raise RuntimeError("Failed to clone %s" % repo)
            if observer:
                observer.did_download_file(repo)

    @staticmethod
    def _git_source(testdir, dirname):
        with changed_directory('%s/%s' % (testdir, dirname)):
            commit_id = subprocess.check_output(
                ['git', 'log', '-1', '--pretty=%H']).strip()
            url = subprocess.check_output(
                ['git', 'config', '--get', 'remote.origin.url']).strip()
            return {
                'project_name': url.rsplit('/')[-1],
                'branch_vcs': 'git',
                'branch_revision': commit_id,
                'branch_url': url,
                }

    def _git_sources(self, testdir):
        """
        Pulls git information from the given local repositories and formats
        them as needed by the software_context's "sources" attribute
        """
        sources = []
        for d in self.git_repos:
            d = self._git_local(d)
            sources.append(self._git_source(testdir, d))
        return sources

    def _bzr_local(self, repo):
        """
        convert bzr url into the local name, it lp:lava-test to lava-test
        """
        repo = repo.replace('lp:', '')
        return repo.split('/')[-1]

    @staticmethod
    def _bzr_source(testdir, dirname):
        with changed_directory('%s/%s' % (testdir, dirname)):
            revno = subprocess.check_output(['bzr', 'revno']).strip()
            url = subprocess.check_output(
                ['bzr', 'config', 'parent_location']).strip()
            return {
                'project_name': dirname,
                'branch_vcs': 'bzr',
                'branch_revision': revno,
                'branch_url': url,
                }

    def _bzr_sources(self, testdir):
        """
        Pulls bzr information from the given local repositories and formats
        them as needed by the software_context's "sources" attribute
        """
        sources = []
        for d in self.bzr_repos:
            d = self._bzr_local(d)
            sources.append(self._bzr_source(testdir, d))
        return sources

    def _bzr_branch(self, observer):
        if not self.bzr_repos:
            return

        for repo in self.bzr_repos:
            if observer:
                observer.about_to_download_file(repo)

            self._run_shell_cmd("bzr branch %s" % repo, observer)

            if not os.path.exists(self._bzr_local(repo)):
                raise RuntimeError("Failed to clone %s" % repo)
            if observer:
                observer.did_download_file(repo)

    def get_software_sources(self, testdir):
        sources = []
        if self.git_repos:
            sources.extend(self._git_sources(testdir))
        if self.bzr_repos:
            sources.extend(self._bzr_sources(testdir))
        return sources

    def _runsteps(self, observer):
        for cmd in self.steps:
            self._run_shell_cmd(cmd, observer)

    def install(self, observer=None):
        self._installdeps(observer)
        self._download(observer)
        self._git_clone(observer)
        self._bzr_branch(observer)
        self._runsteps(observer)
