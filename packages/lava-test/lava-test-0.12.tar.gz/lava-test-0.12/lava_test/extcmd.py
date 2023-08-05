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

from Queue import Queue
import subprocess
import sys
import threading
try:
    import posix
except ImportError:
    posix = None


class ExternalCommand(object):

    def _popen(self, *args, **kwargs):
        if posix:
            kwargs['close_fds'] = True
        return subprocess.Popen(*args, **kwargs)

    def call(self, *args, **kwargs):
        proc = self._popen(*args, **kwargs)
        proc.wait()
        return proc.returncode

    def check_call(self, *args, **kwargs):
        returncode = self.call(*args, **kwargs)
        if returncode != 0:
            raise subprocess.CalledProcessError(
                returncode, kwargs.get("args") or args[0])
        return returncode


class ExternalCommandWithDelegate(ExternalCommand):

    def __init__(self, delegate):
        self._queue = Queue()
        self._delegate = delegate

    def _read_stream(self, stream, stream_name):
        for line in iter(stream.readline, ''):
            cmd = (stream_name, line)
            self._queue.put(cmd)

    def _drain_queue(self):
        while True:
            args = self._queue.get()
            if args is None:
                break
            self._delegate.display_subprocess_output(*args)

    def call(self, *args, **kwargs):
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
        proc = self._popen(*args, **kwargs)
        stdout_reader = threading.Thread(
            target=self._read_stream, args=(proc.stdout, "stdout"))
        stderr_reader = threading.Thread(
            target=self._read_stream, args=(proc.stderr, "stderr"))
        ui_printer = threading.Thread(
            target=self._drain_queue)

        ui_printer.start()
        stdout_reader.start()
        stderr_reader.start()
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.kill()
        finally:
            stdout_reader.join()
            stderr_reader.join()
            self._queue.put(None)
            ui_printer.join()
        return proc.returncode


class DisplayDelegate(object):
    """
    Delegate for displaying command output.

    Perfect companion for ExternalCommandWithDelegate.
    """

    def __init__(self, stdout=None, stderr=None, chain=None):
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.chain = chain

    def display_subprocess_output(self, stream_name, line):
        if stream_name == 'stdout':
            self.stdout.write(line)
        elif stream_name == 'stderr':
            self.stderr.write(line)
        if self.chain:
            self.chain.display_subprocess_output(stream_name, line)
