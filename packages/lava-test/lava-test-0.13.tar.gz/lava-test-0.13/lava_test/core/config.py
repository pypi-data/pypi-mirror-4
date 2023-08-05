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

import os
import json


class LavaTestConfig(object):

    def __init__(self):
        home = os.environ.get('HOME', '/')
        baseconfig = os.environ.get('XDG_CONFIG_HOME',
                     os.path.join(home, '.config'))
        basedata = os.environ.get('XDG_DATA_HOME',
                     os.path.join(home, '.local', 'share'))
        self.configdir = os.path.join(baseconfig, 'lava_test')
        self.installdir = os.path.join(
            basedata, 'lava_test', 'installed-tests')
        self.resultsdir = os.path.join(basedata, 'lava_test', 'results')
        self.registry = self._load_registry()

    @property
    def _registry_pathname(self):
        return os.path.join(self.configdir, "registry.json")

    def _load_registry(self):
        try:
            with open(self._registry_pathname) as stream:
                return json.load(stream)
        except (IOError, ValueError):
            return self._get_default_registry()

    def _save_registry(self):
        if not os.path.exists(self.configdir):
            os.makedirs(self.configdir)
        with open(self._registry_pathname, "wt") as stream:
            json.dump(self.registry, stream, indent=2)

    def _get_default_registry(self):
        return {
            "format": "Lava-Test Test Registry 1.0",
            "providers": [{
                "entry_point": "lava_test.core.providers:BuiltInProvider"
            }, {
                "entry_point": "lava_test.core.providers:PkgResourcesProvider",
                "config": {"namespace": "lava_test.test_definitions"}
            },
            {
                "entry_point": "lava_test.core.providers:RegistryProvider",
                "config": {"entries": []}
            }]
        }

    def get_provider_config(self, entry_point_name):
        if "providers" not in self.registry:
            self.registry["providers"] = []
        for provider_info in self.registry["providers"]:
            if provider_info.get("entry_point") == entry_point_name:
                break
        else:
            provider_info = {"entry_point": entry_point_name}
            self.registry["providers"].append(provider_info)
        if "config" not in provider_info:
            provider_info["config"] = {}
        return provider_info["config"]

_config = None


def get_config():
    global _config
    if _config is not None:
        return _config
    return LavaTestConfig()


def set_config(config):
    global _config
    _config = config
