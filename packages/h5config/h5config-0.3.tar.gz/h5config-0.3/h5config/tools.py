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

"""Tools for setting up a package using config files.

The benefit of subclassing `PackageConfig` over using something like
`configparser` is that you can easily store default `h5config` values
in the configuration file.  Consider the following example:

TODO
> class _MyConfig
"""

import logging as _logging
import os.path as _os_path
import sys as _sys

from . import config as _config
from . import log as _log
from .storage.hdf5 import HDF5_Storage as _HDF5_Storage
from .storage.yaml import YAML_Storage as _YAML_Storage


class PackageConfig (_config.Config):
    """Configure package operation

    This basic implementation just creates and manages a package-wide
    `LOG` instance.  If you create this instance on your own (for
    example, to work around bootstrapping issues), just pass your
    instance in as `logger` when you initialize this class.
    """
    possible_storage = [_HDF5_Storage, _YAML_Storage]
    settings = [
        _config.ChoiceSetting(
            name='log-level',
            help='Module logging level.',
            default=_logging.WARN,
            choices=[
                ('critical', _logging.CRITICAL),
                ('error', _logging.ERROR),
                ('warn', _logging.WARN),
                ('info', _logging.INFO),
                ('debug', _logging.DEBUG),
                ]),
        _config.BooleanSetting(
            name='syslog',
            help='Log to syslog (otherwise log to stderr).',
            default=False),
        ]

    def __init__(self, package_name, namespace=None, logger=None, **kwargs):
        super(PackageConfig, self).__init__(**kwargs)
        self._package_name = package_name
        if not namespace:
            namespace = _sys.modules[package_name]
        self._namespace = namespace
        if not logger:
            logger = _log.get_basic_logger(package_name, level=_logging.WARN)
        self._logger = logger
        if 'LOG' not in dir(namespace):
            namespace.LOG = logger

    def setup(self):
        self._logger.setLevel(self['log-level'])
        if self['syslog']:
            if 'syslog' not in self._logger._handler_cache:
                _syslog_handler = _logging_handlers.SysLogHandler()
                _syslog_handler.setLevel(_logging.DEBUG)
                self._logger._handler_cache['syslog'] = _syslog_handler
                self._logger.handlers = [self._logger._handler_cache['syslog']]
        else:
            self._logger.handlers = [self._logger._handler_cache['stream']]
        self._logger.info('setup {} packge config:\n{}'.format(
                self._package_name, self.dump()))

    def clear(self):
        "Replace self with a non-backed version with default settings."
        super(PackageConfig, self).clear()
        self._storage = None

    def _base_paths(self):
        user_basepath = _os_path.join(
            _os_path.expanduser('~'), '.config', self._package_name)
        system_basepath = _os_path.join('/etc', self._package_name, 'config')
        distributed_basepath =  _os_path.join(
            '/usr', 'share', self._package_name, 'config')
        return [user_basepath, system_basepath, distributed_basepath]

    def load_system(self):
        "Return the best `PackageConfig` match after scanning the filesystem"
        self._logger.info('looking for package config file')
        basepaths = self._base_paths()
        for basepath in basepaths:
            for storage in self.possible_storage:
                filename = '{}.{}'.format(basepath, storage.extension)
                if _os_path.exists(filename):
                    self._logger.info(
                        'base_config file found at {}'.format(filename))
                    self._storage = storage(filename=filename)
                    self.load()
                    self.setup()
                    return
                else:
                    self._logger.debug(
                        'no base_config file at {}'.format(filename))
        # create (but don't save) the preferred file
        basepath = basepaths[0]
        storage = self.possible_storage[0]
        filename = '{}.{}'.format(basepath, storage.extension)
        self._logger.info('new base_config file at {}'.format(filename))
        self._storage = storage(filename=filename)
        self.load()
        self.setup()
