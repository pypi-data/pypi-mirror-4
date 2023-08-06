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

import base64
import datetime
import logging
import os
import uuid

from linaro_dashboard_bundle.io import DocumentIO

from lava_test.core import hwprofile, swprofile
from lava_test.utils import merge_dict, mkdir_p


class TestArtifacts(object):
    """
    Class representing test run artifacts, that is, static leftovers
    independent of the wrapper class that encapsulates test handling.

    .. versionadded:: 0.2
    """

    def __init__(self, test_id, result_id, config):
        self._test_id = test_id
        self._result_id = result_id
        self._config = config
        self._bundle = None

    @classmethod
    def allocate(cls, test_id, config):
        """
        Allocate new test artifacts object that corresponds to the specified
        test_id. This constructs a new result_id and creates the corresponding
        filesystem directory that holds those artifacts.

        .. versionadded:: 0.2
        """
        result_id = (
            "{test_id}.{time.tm_year:04}-{time.tm_mon:02}-{time.tm_mday:02}T"
            "{time.tm_hour:02}:{time.tm_min:02}:{time.tm_sec:02}Z").format(
                test_id=test_id,
                time=datetime.datetime.utcnow().timetuple())
        self = cls(test_id, result_id, config)
        logging.debug("Creating result directory: %r", self.results_dir)
        mkdir_p(self.results_dir)
        return self

    @property
    def test_id(self):
        """
        The ID of the test this run is associated with

        .. versionadded:: 0.2
        """
        return self._test_id

    @property
    def result_id(self):
        """
        The ID of the test run.

        This field is different from analyzer_assigned_uuid at this time but
        may change in the future. The purpose of this field is to identify the
        test run and be able to locate attachments/log files/bundle on the file
        system.

        .. versionadded:: 0.2
        """
        return self._result_id

    @property
    def results_dir(self):
        """
        Pathname of a directory with test run artifacts (log files, crash
        dumps, etc).

        .. versionadded:: 0.2
        """
        return os.path.join(self._config.resultsdir, self.result_id)

    def load_bundle(self):
        """
        Load the results bundle from disk.

        The bundle is also validated if linaro-dashboard-bundle library is
        installed.
        """
        with open(self.bundle_pathname, 'rt') as stream:
            self._bundle = DocumentIO.load(stream)[1]

    def dumps_bundle(self):
        return DocumentIO.dumps(self._bundle)

    def save_bundle(self):
        """
        Save the results bundle to the disk

        The bundle is also validated if linaro-dashboard-bundle library is
        installed.
        """
        self.save_bundle_as(self.bundle_pathname)

    def save_bundle_as(self, pathname):
        """
        Save the results bundle to the specified file on disk.

        The bundle should have been created or loaded earlier
        """
        with open(pathname, 'wt') as stream:
            DocumentIO.dump(stream, self._bundle)

    @property
    def bundle(self):
        """
        The deserialized bundle object.

        This can be either created with create_bundle() or loaded
        from disk with load_bundle()
        """
        return self._bundle

    def create_initial_bundle(self,
                      skip_software_context=False,
                      skip_hardware_context=False,
                      time_check_performed=False,
                      analyzer_assigned_uuid=None,
                      test=None):
        """
        Create the bundle object.

        This creates a typical bundle structure. Optionally it can also add
        software and hardware context information.

        For a complete bundle you may want to add attachments and incorporate
        parse results by calling appropriate methods after loading or creating
        the initial bundle.
        """
        TIMEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
        # Generate UUID and analyzer_assigned_date for the test run
        if analyzer_assigned_uuid is None:
            analyzer_assigned_uuid = str(uuid.uuid1())
        analyzer_assigned_date = datetime.datetime.utcnow()
        # Create basic test run structure
        test_run = {
            'test_id': self.test_id,
            'analyzer_assigned_date': analyzer_assigned_date.strftime(
                TIMEFORMAT),
            'analyzer_assigned_uuid': analyzer_assigned_uuid,
            'time_check_performed': time_check_performed,
            "test_results": [],
            "attachments": [],
        }
        # Store hardware and software context if requested
        if not skip_software_context:
            test_run['software_context'] = swprofile.get_software_context(
                test=test)
        if not skip_hardware_context:
            test_run['hardware_context'] = hwprofile.get_hardware_context()
        # Create the bundle object
        self._bundle = {
            'format': 'Dashboard Bundle Format 1.3',
            'test_runs': [test_run]}

    @property
    def test_run(self):
        try:
            return self._bundle["test_runs"][0]
        except KeyError:
            raise AttributeError("test_run can be accessed only after you load"
                                 " or create an initial bundle")

    def attach_file(self, real_pathname, stored_pathname, mime_type):
        """
        Append an attachment to the test run.

        The file is only attached if real_pathname designates an existing,
        nonempty file. If the mime_type starts with 'text/' the file is opened
        in text mode, otherwise binary mode is used.
        """
        if not os.path.exists(real_pathname):
            return
        if mime_type.startswith('text/'):
            mode = 'rt'
        else:
            mode = 'rb'
        with open(real_pathname, mode) as stream:
            data = stream.read()
        if not data:
            return
        self.test_run['attachments'].append({
            "pathname": stored_pathname,
            "mime_type": mime_type,
            "content": base64.standard_b64encode(data)})

    def incorporate_parse_results(self, parse_results):
        """
        Merge the data returned by the test parser into the current test run.

        Non-overlapping data is simply added. Overlapping data is either merged
        (lists are extended, dictionaries are recursively merged) or
        overwritten (all other types).
        """
        assert isinstance(parse_results, dict)
        # Use whatever the parser gave us to improve the results
        logging.debug("Using parser data to enrich test run details")
        merge_dict(self.test_run, parse_results)

    def attach_standard_files_to_bundle(self):
        """
        Attach standard output and standard error log files to the bundle.

        Both files are only attached if exist and non-empty. The attachments
        are actually associated with a test run, not a bundle, but the
        description is good enough for simplicity.
        """
        self.attach_file(self.stdout_pathname, "testoutput.log", "text/plain")
        self.attach_file(self.stderr_pathname, "testoutput.err", "text/plain")

    @property
    def bundle_pathname(self):
        """
        Pathname of the result bundle.

        The bundle contains the snapshot of environment information as well as
        test identity and is created when you invoke ITest.run().

        The bundle file name is always "testdata.json"

        .. versionadded:: 0.2
        """
        return self.get_artefact_pathname("testdata.json")

    @property
    def stdout_pathname(self):
        """
        Pathname of the log file of the standard output as returned by the test
        program.

        The log file name is always "testoutput.log"

        .. versionadded:: 0.2
        """
        return self.get_artefact_pathname("testoutput.log")

    @property
    def stderr_pathname(self):
        """
        Pathname of the log file of the standard output as returned by the test
        program.

        The log file name is always "testoutput.err"

        .. versionadded:: 0.2
        """
        return self.get_artefact_pathname("testoutput.err")

    def get_artefact_pathname(self, artefact_name):
        """
        Return a pathname of a test run artefact file.

        This is more useful than hard-coding the path as it allows the test
        runner not to worry about the location of the results directory.

        .. versionadded:: 0.2
        """
        return os.path.join(self.results_dir, artefact_name)
