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

import os as _os
import os.path as _os_path
import sys as _sys
import types as _types


class Storage (object):
    "A storage bakend for loading and saving `Config` instances"
    def load(self, config, merge=False, **kwargs):
        if merge:
            self.clear()
        self._load(config=config, **kwargs)
        config.set_storage(storage=self)

    def _load(self, config, **kwargs):
        raise NotImplementedError()

    def save(self, config, merge=False, **kwargs):
        if merge:
            self.clear()
        self._save(config=config, **kwargs)
        config._storage = self

    def _save(self, config, **kwargs):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()


class FileStorage (Storage):
    "`Config` storage backend by a single file"
    extension = None

    def __init__(self, filename=None):
        self._filename = filename

    def _create_basedir(self, filename):
        dirname = _os_path.dirname(filename)
        if dirname and not _os_path.isdir(dirname):
            _os.makedirs(dirname)


def is_string(x):
    if _sys.version_info >= (3,):
        return isinstance(x, (bytes, str))
    else:  # Python 2 compatibility
        return isinstance(x, _types.StringTypes)
