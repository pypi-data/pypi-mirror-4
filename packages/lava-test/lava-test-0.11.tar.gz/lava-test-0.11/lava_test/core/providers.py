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

from lava_test.api.core import ITestProvider
from lava_test.core.config import get_config
from lava_test.core.tests import DeclarativeTest
from lava_test.utils import Cache

import logging


class BuiltInProvider(ITestProvider):
    """
    Test provider that provides tests shipped in the Lava-Test source tree
    """

    _builtin_tests = [
        'bluetooth_enablement',
        'bootchart',
        'device_tree',
        'insanity',
        'e2eaudiotest',
        'firefox',
        'gatortests',
        'glmemperf',
        'gmpbench',
        'gtkperf',
        'leb_basic_graphics',
        'lt_ti_lava',
        'ltp',
        'ltp-snowball-tests',
        'lttng',
        'peacekeeper',
        'perf',
        'posixtestsuite',
        'pwrmgmt',
        'pybench',
        'smem',
        'stream',
        'tiobench',
        'tjbench',
        'x11perf',
        'xrestop',
        'wifi_enablement',
    ]

    def __init__(self, config):
        pass

    @property
    def description(self):
        return "Tests built directly into LAVA Test:"

    def __iter__(self):
        return iter(self._builtin_tests)

    def __getitem__(self, test_id):
        if test_id not in self._builtin_tests:
            raise KeyError(test_id)
        module = __import__("lava_test.test_definitions.%s" % test_id,
                            fromlist=[''])
        return module.testobj


class PkgResourcesProvider(ITestProvider):
    """
    Test provider that provides tests declared in pkg_resources working_set

    By default it looks at the 'lava_test.test_definitions' name space but it
    can be changed with custom 'namespace' configuration entry.
    """

    def __init__(self, config):
        self._config = config

    @property
    def namespace(self):
        return self._config.get("namespace", "lava_test.test_definitions")

    @property
    def description(self):
        return ("Tests provided by installed python packages"
                " (from namespace {0}):").format(self.namespace)

    def __iter__(self):
        from pkg_resources import working_set
        for entry_point in working_set.iter_entry_points(self.namespace):
            yield entry_point.name

    def __getitem__(self, test_name):
        from pkg_resources import working_set
        for entry_point in working_set.iter_entry_points(self.namespace,
                                                         test_name):
            return entry_point.load().testobj
        raise KeyError(test_name)


class RegistryProvider(ITestProvider):
    """
    Test provider that provides declarative tests listed in the test registry.
    """
    def __init__(self, config):
        self._config = config
        self._cache = None

    @property
    def entries(self):
        """
        List of URLs to DeclarativeTest description files
        """
        return self._config.get("entries", [])

    @property
    def description(self):
        return "Tests provided by LAVA Test registry:"

    @classmethod
    def register_remote_test(self, test_url):
        config = get_config()  # This is a different config object from
                               # self._config
        provider_config = config.get_provider_config(
            "lava_test.core.providers:RegistryProvider")
        if "entries" not in provider_config:
            provider_config["entries"] = []
        if test_url not in provider_config["entries"]:
            provider_config["entries"].append(test_url)
            config._save_registry()
        else:
            raise ValueError("This test is already registered")

    @classmethod
    def unregister_remote_test(self, test_url):
        # This is a different config object from self._config
        config = get_config()
        provider_config = config.get_provider_config(
            "lava_test.core.providers:RegistryProvider")
        provider_config.get("entries", []).remove(test_url)
        config._save_registry()

    def _load_remote_test(self, test_url):
        """
        Load DeclarativeTest from a (possibly cached copy of) test_url
        """
        cache = Cache.get_instance()
        with cache.open_cached_url(test_url) as stream:
            return DeclarativeTest.load_from_stream(stream)

    def _fill_cache(self):
        """
        Fill the cache of all remote tests
        """
        if self._cache is not None:
            return
        self._cache = {}
        for test_url in self.entries:
            try:
                test = self._load_remote_test(test_url)
                if test.test_id in self._cache:
                    raise ValueError(
                        "Duplicate test %s declared" % test.test_id)
                self._cache[test.test_id] = test
            except IOError as exc:
                logging.warning(
                    "Unable to load test definition from %r: %r",
                    test_url, exc)
                if hasattr(exc, 'reason'):
                    logging.warning("Error reason: %r", exc.reason)
                elif hasattr(exc, 'code'):
                    logging.warning('Error code: %r', exc.code)
            except Exception as exc:
                # This can be a number of things, including URL errors, JSON
                # errors and validation errors
                logging.warning(
                    'Unable to load test definition from %r: %r',
                    test_url, exc)

    def __iter__(self):
        self._fill_cache()
        for test_id in self._cache.iterkeys():
            yield test_id

    def __getitem__(self, test_id):
        self._fill_cache()
        return self._cache[test_id]
