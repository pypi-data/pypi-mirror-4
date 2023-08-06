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

"""HDF5 backend implementation
"""

from __future__ import absolute_import

import os.path as _os_path

import yaml as _yaml  # global PyYAML module

from .. import LOG as _LOG
from .. import config as _config
from . import FileStorage as _FileStorage
from . import is_string as _is_string


class _YAMLDumper (_yaml.SafeDumper):
    def represent_bool(self, data):
        "Use yes/no instead of the default true/false"
        if data:
            value = 'yes'
        else:
            value = 'no'
        return self.represent_scalar('tag:yaml.org,2002:bool', value)


_YAMLDumper.add_representer(bool, _YAMLDumper.represent_bool)


class YAML_Storage (_FileStorage):
    """Back a `Config` class with a YAML file.

    >>> import os
    >>> from ..test import TestConfig
    >>> import os.path
    >>> import tempfile
    >>> fd,filename = tempfile.mkstemp(
    ...     suffix='.'+YAML_Storage.extension, prefix='pypiezo-')
    >>> os.close(fd)

    >>> c = TestConfig(storage=YAML_Storage(filename=filename))
    >>> c.load()

    Saving writes all the config values to disk.

    >>> c['alive'] = True
    >>> c.save()
    >>> print(open(filename, 'r').read())  # doctest: +REPORT_UDIFF
    age: 1.3
    alive: yes
    bids:
    - 5.4
    - 3.2
    - 1
    children: ''
    claws:
    - 1
    - 2
    daisies: 13
    name: ''
    species: Norwegian Blue
    spouse: ''
    words:
    - cracker
    - wants
    <BLANKLINE>

    Loading reads the config files from disk.

    >>> c.clear()
    >>> c['alive']
    False
    >>> c.load()
    >>> c['alive']
    True

    Cleanup our temporary config file.

    >>> os.remove(filename)
    """
    extension = 'yaml'
    dumper = _YAMLDumper

    def _load(self, config):
        if not _os_path.exists(self._filename):
            open(self._filename, 'a').close()
        with open(self._filename, 'r') as f:
            data = _yaml.safe_load(f)
        if data == None:
            return  # empty file
        return self._from_dict(config, data)

    @staticmethod
    def _from_dict(config, data):
        settings = dict([(s.name, s) for s in config.settings])
        for key,value in data.items():
            setting = settings[key]
            if isinstance(setting, (_config.BooleanSetting,
                                    _config.NumericSetting,
                                    _config.ListSetting,
                                    _config.IntegerListSetting,
                                    _config.FloatListSetting)):
                if _is_string(value):
                    # older versions of h5config
                    value = s.convert_from_text(value)
                v = value
            elif isinstance(setting, _config.ConfigListSetting) and value:
                values = []
                for v in value:
                    values.append(YAML_Storage._from_dict(
                            setting.config_class(), v))
                v = values
            elif isinstance(setting, _config.ConfigSetting) and value:
                v = YAML_Storage._from_dict(setting.config_class(), value)
            else:
                v = setting.convert_from_text(value)
            config[key] = v
        return config

    def _save(self, config):
        self._create_basedir(filename=self._filename)
        data = self._to_dict(config)
        with open(self._filename, 'w') as f:
            _yaml.dump(data, stream=f, Dumper=self.dumper,
                       default_flow_style=False)

    @staticmethod
    def _to_dict(config):
        data = {}
        settings = dict([(s.name, s) for s in config.settings])
        for key,value in config.items():
            if key in settings:
                setting = settings[key]
                if isinstance(setting, (_config.BooleanSetting,
                                        _config.NumericSetting,
                                        _config.ListSetting,
                                        _config.IntegerListSetting,
                                        _config.FloatListSetting)):
                    v = value
                elif isinstance(setting, _config.ConfigListSetting) and value:
                    values = []
                    for v in value:
                        values.append(YAML_Storage._to_dict(v))
                    v = values
                elif isinstance(setting, _config.ConfigSetting) and value:
                    v = YAML_Storage._to_dict(value)
                else:
                    v = setting.convert_to_text(value)
                data[key] = v
        return data
