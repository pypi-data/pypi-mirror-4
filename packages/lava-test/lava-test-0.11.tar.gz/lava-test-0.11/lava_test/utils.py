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

import contextlib
import hashlib
import logging
import os
import shutil
import urllib2
import urlparse

_fake_files = None
_fake_paths = None
_fake_machine = None


def geturl(url, path=""):
    urlpath = urlparse.urlsplit(url).path
    filename = os.path.basename(urlpath)
    if path:
        filename = os.path.join(path, filename)
    fd = open(filename, "w")
    try:
        response = urllib2.urlopen(urllib2.quote(url, safe=":/"))
        fd = open(filename, 'wb')
        shutil.copyfileobj(response, fd, 0x10000)
        fd.close()
        response.close()
    except:
        raise RuntimeError("Could not retrieve %s" % url)
    return filename


def write_file(data, path):
    with open(path, "w") as fd:
        fd.write(data)


def read_file(path):
    global _fake_files
    global _fake_paths
    if _fake_files is not None:
        if path in _fake_files:
            return _fake_files[path]
    if _fake_paths is not None:
        if path in _fake_paths:
            path = _fake_paths[path]
    with open(path, 'rb') as stream:
        return stream.read()


def fake_file(path, data=None, newpath=None):
    """
    Set up a fake file to be read with read_file() in testing
    If data is specified, the string passed as data will be returned instead
    if newpath is specified, the file attempted to be read will be replaced
    by newfile
    """
    global _fake_files
    global _fake_paths
    if data is not None:
        if _fake_files is None:
            _fake_files = {}
        _fake_files[path] = data
    if newpath is not None:
        if _fake_paths is None:
            _fake_paths = {}
        _fake_paths[path] = newpath


def fake_machine(type):
    """
    Set up a fake machine type for testing
    """
    global _fake_machine
    _fake_machine = type


def clear_fakes():
    global _fake_files
    global _fake_paths
    _fake_files = {}
    _fake_paths = {}


def clear_fake_machine():
    global _fake_machine
    _fake_machine = None


def get_machine_type():
    """
    Return the machine type
    """
    global _fake_machine
    if _fake_machine is None:
        return os.uname()[-1]
    return _fake_machine


def mkdir_p(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


@contextlib.contextmanager
def changed_directory(dirname, make_if_needed=True):
    """
    A context manager for running a piece of code in another
    directory. The directory is created if needed (by default, can
    be changed with make_if_needed).
    """
    orig_dir = os.getcwd()
    if make_if_needed:
        mkdir_p(dirname)
    logging.info("Changing directory to %r", dirname)
    os.chdir(dirname)
    try:
        yield
    finally:
        logging.info("Changing directory to %r", orig_dir)
        os.chdir(orig_dir)


def merge_dict(merge_into, merge_from):
    """
    Merge two dictionaries recursively:

        1) Simple values are overwritten with a logging.warning() message
        2) Lists are appended
        3) Dictionaries are merged recursively
    """
    assert isinstance(merge_into, dict)
    assert isinstance(merge_from, dict)
    for key in merge_from.iterkeys():
        if key in merge_into:
            if (isinstance(merge_from[key], dict)
                and isinstance(merge_into[key], dict)):
                merge_dict(merge_into[key], merge_from[key])
            elif (isinstance(merge_from[key], list)
                  and isinstance(merge_into[key], list)):
                merge_into[key].extend(merge_from[key])
            else:
                logging.warning(
                    "Overwriting existing value of %r:"
                    "%r overwritten with %r",
                    key, merge_into[key], merge_from[key])
                merge_into[key] = merge_from[key]
        else:
            merge_into[key] = merge_from[key]


class Cache(object):
    """
    Simple open-cached-URL class
    """

    _instance = None

    def __init__(self):
        home = os.environ.get('HOME', '/')
        basecache = os.environ.get('XDG_CACHE_HOME',
                     os.path.join(home, '.cache'))
        self.cache_dir = os.path.join(basecache, 'lava_test')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _open_cached(self, key, mode="r"):
        """
        Acts like open() but the pathname is relative to the
        lava_test-specific cache directory.
        """

        if "w" in mode and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        if os.path.isabs(key):
            raise ValueError("key cannot be an absolute path")

        stream = open(os.path.join(self.cache_dir, key), mode)
        return stream

    def _key_for_url(self, url):
        return hashlib.sha1(url).hexdigest()

    def _refresh_url_cache(self, key, url):
        with contextlib.nested(
            contextlib.closing(urllib2.urlopen(url)),
            self._open_cached(key, "wb")) as (in_stream, out_stream):
            out_stream.write(in_stream.read())

    @contextlib.contextmanager
    def open_cached_url(self, url):
        """
        Like urlopen.open() but the content may be cached.
        """
        # Do not cache local files, this is not what users would expect

        if url.startswith("file://"):
            stream = urllib2.urlopen(url)
        else:
            key = self._key_for_url(url)
            try:
                stream = self._open_cached(key, "rb")
            except IOError:
                self._refresh_url_cache(key, url)
                stream = self._open_cached(key, "rb")
        try:
            yield stream
        finally:
            stream.close()
