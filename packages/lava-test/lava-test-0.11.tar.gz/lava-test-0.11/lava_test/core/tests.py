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

from __future__ import absolute_import

import json
import logging
import os
import shutil

from lava_test.api.core import ITest
from lava_test.core.artifacts import TestArtifacts
from lava_test.core.config import get_config
from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser, NativeTestParser
from lava_test.core.runners import TestRunner
from lava_test.utils import changed_directory


class Test(ITest):
    """
    Reusable class for defining tests.

    This class uses composition instead of inheritance. You should be able to
    customize the parts you care about by providing delegate objects. This
    class can be used by test definition files to create an object that
    contains the building blocks for installing tests, running them, and
    parsing the results.

    :ivar test_id:
        Name of the test or test suite
    :ivar test_version:
        Version of the test or test suite
    :ivar installer:
        ITestInstaller instance to use
    :ivar runner:
        ITestRunner instance to use
    :ivar parser:
        ITestParser instance to use
    """

    def __init__(self, test_id, test_version=None, installer=None, runner=None,
                 parser=None, default_options=None):
        self._test_id = test_id
        self._test_version = test_version
        # Delegate objects
        self.installer = installer
        self.runner = runner
        self.parser = parser
        self.default_options = default_options

        # Config instance
        self._config = get_config()

    def __repr__(self):
        return ("<%s test_id=%r test_version=%r installer=%r runner=%r"
                " parser=%r>") % (
                    self.__class__.__name__, self.test_id, self.test_version,
                    self.installer, self.runner, self.parser)

    @property
    def test_id(self):
        """
        Return the ID of the test.
        """
        return self._test_id

    @property
    def test_version(self):
        """
        Return the version of the test
        """
        return self._test_version

    @property
    def install_dir(self):
        """
        Pathname of a directory with binary and data files installed by the
        test.

        .. versionadded:: 0.2
        """
        return os.path.join(self._config.installdir, self.test_id)

    @property
    def is_installed(self):
        return os.path.exists(self.install_dir)

    def install(self, observer=None):
        if self.is_installed:
            raise RuntimeError(
                "%s is already installed" % self.test_id)
        if not self.installer:
            raise RuntimeError(
                "no installer defined for '%s'" % self.test_id)
        with changed_directory(self.install_dir):
            try:
                logging.debug(
                    "Invoking %r.install(...)", self.installer)
                self.installer.install(observer)
            except:
                self.uninstall()
                raise

    def uninstall(self):
        logging.debug("Removing test %r", self.test_id)
        if os.path.exists(self.install_dir):
            shutil.rmtree(self.install_dir)

    def run(self, observer=None, test_options=None):
        if not self.runner:
            raise RuntimeError(
                "no test runner defined for '%s'" % self.test_id)
        artifacts = TestArtifacts.allocate(self.test_id, self._config)
        with changed_directory(self.install_dir):
            logging.debug("Invoking %r.run(...)", self.runner)
            run_fail = self.runner.run(artifacts, observer, test_options)

        return artifacts, run_fail

    def parse(self, artifacts):
        if self.parser:
            logging.debug("Invoking %r.parse()", self.parser)
            with changed_directory(artifacts.results_dir, False):
                self.parser.parse(artifacts)
            return self.parser.results


class DeclarativeTest(Test):
    """
    Declaretive ITest implementation.

    Declarative test is like :class:`lava_test.core.tests.Test` but cannot
    contain any python code and is completely encapsulated in a .json file.

    The idea is to write .json files that assemble a Test instance using
    readily-available TestInstaller, TestRunner and TestParser subclasses.
    """

    def __init__(self, about):
        self.about = about
        super(DeclarativeTest, self).__init__(self.about.get('test_id'))
        self.installer = TestInstaller(**self.about.get('install', {}))
        self.runner = TestRunner(**self.about.get('run', {}))
        if self.about.get('parse', {}).get('native', False) is True:
            self.parser = NativeTestParser(self)
        else:
            self.parser = TestParser(**self.about.get('parse', {}))

    @classmethod
    def load_from_stream(cls, stream):
        return cls(json.load(stream))

    def save_to_stream(self, stream):
        json.dumps(self.about, stream, indent="2")
