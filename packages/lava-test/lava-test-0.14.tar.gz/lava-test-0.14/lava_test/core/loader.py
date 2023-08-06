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
from lava_test.core.config import get_config

import logging


class TestLoader(object):
    """
    Test loader.

    Encapsulates LAVA Test's knowledge of available tests.

    Test can be loaded by name with
    :meth:`lava_test.core.loader.TestLoader.__getitem__()`. Test can also be
    listed by :meth:`lava_test.core.loader.TestLoader.get_providers()` and then
    iterating over tests returned by each provider.
    """

    def __init__(self, config):
        self._config = config

    def get_providers(self):
        """
        Return a generator of available providers
        """
        import pkg_resources
        for provider_info in self._config.registry.get("providers", []):
            entry_point_name = provider_info.get("entry_point")
            module_name, attrs = entry_point_name.split(':', 1)
            attrs = attrs.split('.')
            try:
                entry_point = pkg_resources.EntryPoint(
                    entry_point_name, module_name, attrs,
                    dist=pkg_resources.get_distribution("lava-test"))
                provider_cls = entry_point.load()
                provider = provider_cls(provider_info.get("config", {}))
                yield provider
            except pkg_resources.DistributionNotFound:
                raise RuntimeError(
                    "lava-test is not properly set up."
                    " Please read the README file")
            except ImportError:
                logging.warning("Couldn't load module: %s", module_name)
                logging.warning(
                    "The configuration may need updating, it is stored in %r",
                    get_config().configdir)

    def __getitem__(self, test_id):
        """
        Lookup a test with the specified test_id
        """
        for provider in self.get_providers():
            try:
                return provider[test_id]
            except KeyError:
                pass
        raise KeyError(test_id)

    def get_test_by_name(self, test_id):
        """
        Lookup a test with the specified name

        .. deprecated:: 0.2
            Use __getitem__ instead
        """
        for provider in self.get_providers():
            try:
                return provider[test_id]
            except KeyError:
                pass
        raise ValueError("No such test %r" % test_id)
