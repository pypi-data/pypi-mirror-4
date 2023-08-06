# Copyright (C) 2011-2012 W. Trevor King <wking@tremily.us>
#
# This file is part of h5config.
#
# h5config is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# h5config is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# h5config.  If not, see <http://www.gnu.org/licenses/>.

from .log import get_basic_logger as _get_basic_logger


__version__ = '0.3'

LOG = _get_basic_logger(__name__)

from .tools import PackageConfig as _PackageConfig


package_config = _PackageConfig(package_name=__name__, logger=LOG)
package_config.load_system()
