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

import logging
import logging.config

from lava_tool.dispatcher import LavaDispatcher, run_with_dispatcher_class


class LAVATestDispatcher(LavaDispatcher):

    toolname = 'lava_test'
    description = """
    LAVA Test wrapper framework
    """
    epilog = """
    Please report all bugs using the Launchpad bug tracker:
    http://bugs.launchpad.net/lava-test/+filebug
    """


def main():
    # default logging level is warning. -v or --verbose will change it to debug
    # (in Command class).
    FORMAT = '<LAVA_TEST>%(asctime)s %(levelname)s: %(message)s'
    DATEFMT = '%Y-%m-%d %I:%M:%S %p'
    logging.basicConfig(format=FORMAT, datefmt=DATEFMT)
    logging.root.setLevel(logging.WARNING)
    return run_with_dispatcher_class(LAVATestDispatcher)


if __name__ == '__main__':
    raise SystemExit(main())
