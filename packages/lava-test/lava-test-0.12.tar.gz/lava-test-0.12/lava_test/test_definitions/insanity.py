# Copyright (c) 2010 Linaro
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
#

"""
GStreamer QA system

**URL:** http://git.collabora.co.uk/?p=user/edward/gst-qa-system;a=summary

**Default options:** None
"""

import os
import simplejson
import gzip
import base64

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test


MAX_TEST_CASE_ID_LEN = 100
MAX_ATTR_KEY_LEN = 32
MAX_ATTR_VAL_LEN = 512

MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024

SETTINGS = "/usr/share/insanity/web/settings.py"

# Re-running failing tests is expensive, as it produces very large log files.
# Only remove --no-reruns if you have a small number of failing tests.
RUNSTEPS = [
    "rm -f testrun.db",
    "gst-media-test --no-reruns -t playbin-test --settings %s" % SETTINGS,
    "gst-media-test --no-reruns -t full-gnlfilesource-scenario " \
    "--settings %s" % SETTINGS,
    "gst-media-test --no-reruns -t simple-encoder-scenario",
    "echo ////////////////////",
    "insanity-dumpresults-json testrun.db --all",
]


class InsanityParser(TestParser):

    def parse(self, artifacts):
        filename = "testoutput.log"
        with open(filename) as stream:
            while not stream.readline().startswith("//////////"):
                pass
            results = simplejson.load(stream)

        self._results = results
        self.fixresults({"pass": "pass", "fail": "fail",
                "skip": "skip", "expected-failure": "pass"})
        self.fixlengths()
        self.attach_logfiles()

    def fixlengths(self):
        for t in self.results['test_results']:
            if "test_case_id" in t:
                if len(t["test_case_id"]) > MAX_TEST_CASE_ID_LEN:
                    t["test_case_id"] = \
                            t["test_case_id"][-MAX_TEST_CASE_ID_LEN:]
            if "attributes" in t:
                attributes = t["attributes"]
                for k, v in attributes.items():
                    if len(k) > MAX_ATTR_KEY_LEN:
                        attributes.pop(k)
                        # start includes namespace info
                        k = k[:MAX_ATTR_KEY_LEN]
                        attributes[k] = v
                    if len(v) > MAX_ATTR_VAL_LEN:
                        # end tends to be more useful than the start.
                        attributes[k] = v[-MAX_ATTR_VAL_LEN:]

    def attach_logfiles(self):
        # FIXME: this should use artifacts.attach_file()
        attachments = []
        mime_type = "text/plain"
        total_attachment_size = 0

        for test in self.results["test_results"]:
            pathname = test.get("log_filename", "")
            if not pathname:
                continue
            if not os.path.exists(pathname):
                print "%r not found: skipping." % pathname
                continue

            if pathname.endswith(".gz"):
                stream = gzip.open(pathname, 'rb')
            else:
                stream = open(pathname)

            output_text = stream.read()
            stream.close()

            total_attachment_size += len(output_text)
            if total_attachment_size > MAX_ATTACHMENT_SIZE:
                break

            attachments.append({
                    "pathname": pathname,
                    "mime_type": mime_type,
                    "content":  base64.standard_b64encode(output_text)
                })

        self.results.setdefault("attachments", []).extend(attachments)

    def fixresults(self, fixupdict):
        """Convert results to a known, standard format

        pass it a dict of keys/values to replace
        For instance:
            {"TPASS":"pass", "TFAIL":"fail"}
        This is really only used for qualitative tests
        """
        for t in self.results['test_results']:
            if "result" in t:
                t['result'] = fixupdict[t['result']]


installer = TestInstaller(
    deps=[
        "insanity-tools",
        "samplemedia-minimal",
        "gstreamer0.10-plugins-base",  # videotestsrc et al
        "gstreamer0.10-plugins-good",  # matroskademux et al
        "gstreamer0.10-plugins-bad",
        "gstreamer0.10-plugins-ugly",  # asfdemux et al
        "gstreamer0.10-ffmpeg",  # ffdec_h264 et al
        "gstreamer0.10-gnonlin",  # gnlfilesource
        "gdb",  # debugging backtraces
    ]
)
runner = TestRunner(RUNSTEPS)
parser = InsanityParser()

testobj = Test(
    test_id="insanity",
    installer=installer,
    runner=runner,
    parser=parser)
