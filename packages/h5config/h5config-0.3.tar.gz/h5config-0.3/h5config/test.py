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

"""Define a test config object using all the setting types

The first time you a storage backend, the file it creates will
probably be empty or not exist.

>>> import os
>>> import tempfile
>>> from h5config.storage.hdf5 import pprint_HDF5, HDF5_Storage

>>> fd,filename = tempfile.mkstemp(suffix='.h5', prefix='h5config-')
>>> os.close(fd)

>>> c = TestConfig(storage=HDF5_Storage(filename=filename, group='/base'))
>>> c.load()

Loading will create a stub group group if it hadn't existed before.

>>> pprint_HDF5(filename)
/
  /base

Saving fills in all the config values.

>>> c['syslog'] = True
>>> c.save()
>>> pprint_HDF5(filename)  # doctest: +REPORT_UDIFF, +ELLIPSIS
/
  /base
    <HDF5 dataset "age": shape (), type "<f8">
      1.3
    <HDF5 dataset "alive": shape (), type "|b1">
      False
    <HDF5 dataset "bids": shape (3,), type "<f8">
      [ 5.4  3.2  1. ]
    <HDF5 dataset "children": shape (), type "|S1">
<BLANKLINE>
    <HDF5 dataset "claws": shape (2,), type "<i8">
      [1 2]
    <HDF5 dataset "daisies": shape (), type "<i...">
      13
    <HDF5 dataset "name": shape (), type "|S1">
<BLANKLINE>
    <HDF5 dataset "species": shape (), type "|S14">
      Norwegian Blue
    <HDF5 dataset "spouse": shape (), type "|S1">
<BLANKLINE>
    <HDF5 dataset "words": shape (2,), type "|S7">
      ['cracker' 'wants']

If you want more details, you can dump with help strings.

>>> print(c.dump(help=True))  # doctest: +REPORT_UDIFF, +NORMALIZE_WHITESPACE
name:                    (The parrot's name.  Default: .)
species: Norwegian Blue  (Type of parrot.  Default: Norwegian Blue.
                          Choices: Norwegian Blue, Macaw)
alive: no                (The parrot is alive.  Default: no.  Choices: yes, no)
daisies: 13              (Number of daisies pushed up by the parrot.
                          Default: 13.)
age: 1.3                 (Parrot age in years  Default: 1.3.)
words: cracker,wants     (Words known by the parrot.  Default: cracker,wants.)
claws: 1,2               (Claws on each foot.  Default: 1,2.)
bids: 5.4,3.2,1          (Prices offered for parrot.  Default: 5.4,3.2,1.)
spouse:                  (This parrot's significant other.  Default: .)
children:                (This parrot's children.  Default: .)

As you can see from the `age` setting, settings also support `None`,
even if they have numeric types.

Cleanup our temporary config file.

>>> os.remove(filename)
"""

import os as _os
import sys as _sys
import tempfile as _tempfile

from . import LOG as _LOG
from . import config as _config
from .storage import FileStorage as _FileStorage
from .storage.hdf5 import HDF5_Storage
from .storage.yaml import YAML_Storage


class TestConfig (_config.Config):
    "Test all the setting types for the h5config module"
    settings = [
        _config.Setting(
            name='name',
            help="The parrot's name."),
        _config.ChoiceSetting(
            name='species',
            help='Type of parrot.',
            default=0,
            choices=[('Norwegian Blue', 0), ('Macaw', 1)]),
        _config.BooleanSetting(
            name='alive',
            help='The parrot is alive.',
            default=False),
        _config.IntegerSetting(
            name='daisies',
            help="Number of daisies pushed up by the parrot.",
            default=13),
        _config.FloatSetting(
            name='age',
            help='Parrot age in years',
            default=1.3),
        _config.ListSetting(
            name='words',
            help='Words known by the parrot.',
            default=['cracker', 'wants']),
        _config.IntegerListSetting(
            name='claws',
            help='Claws on each foot.',
            default=[1, 2]),
        _config.FloatListSetting(
            name='bids',
            help='Prices offered for parrot.',
            default=[5.4, 3.2, 1]),
        _config.ConfigSetting(
            name='spouse',
            help="This parrot's significant other."),
        _config.ConfigListSetting(
            name='children',
            help="This parrot's children."),
        ]

# must define self-references after completing the TestConfig class
for s in TestConfig.settings:
    if s.name in ['spouse', 'children']:
        s.config_class = TestConfig


def _alternative_test_config(name):
    ret = TestConfig()
    ret['name'] = name
    return ret

_ALTERNATIVES = {  # alternative settings for testing
    'name': 'Captain Flint',
    'species': 1,
    'alive': True,
    'daisies': None,
    'age': None,
    'words': ['arrrr', 'matey'],
    'claws': [3, 0],
    'bids': [],
    'spouse': _alternative_test_config(name='Lory'),
    'children': [_alternative_test_config(name=n)
                 for n in ['Washington Post', 'Eli Yale']],
    }
# TODO: share children with spouse to test references

def test(storage=None):
    if storage is None:
        storage = [HDF5_Storage, YAML_Storage]
        for s in storage:
            test(storage=s)
        return
    _LOG.debug('testing {}'.format(storage))
    _basic_tests(storage)
    if issubclass(storage, _FileStorage):
        _file_storage_tests(storage)

def _basic_tests(storage):
    pass

def _file_storage_tests(storage):
    fd,filename = _tempfile.mkstemp(
        suffix='.'+storage.extension, prefix='h5config-')
    _os.close(fd)
    try:
        c = TestConfig(storage=storage(filename=filename))
        c.dump()
        c.save()
        c.load()
        nd = list(_non_defaults(c))
        assert not nd, (storage, nd)
        for key,value in _ALTERNATIVES.items():
            c[key] = value
        c.dump()
        c.save()
        na = dict(_non_alternatives(c))
        assert not na, (storage, na)
        c.clear()
        nd = list(_non_defaults(c))
        assert not nd, (storage, nd)
        c.load()
        na = dict(_non_alternatives(c))
        assert not na, (storage, na)
    finally:
        _os.remove(filename)

def _non_defaults(config):
    for setting in TestConfig.settings:
        value = config[setting.name]
        if value != setting.default:
            yield (setting.name, value)

def _non_alternatives(config, alternatives=None):
    if alternatives is None:
        alternatives = _ALTERNATIVES
    for setting in TestConfig.settings:
        value = config[setting.name]
        alt = alternatives[setting.name]
        if value != alt:
            _LOG.error('{} value missmatch: {} vs {}'.format(
                    setting.name, value, alt))
            yield (setting.name, value)
        elif type(value) != type(alt):
            _LOG.error('{} type missmatch: {} vs {}'.format(
                    setting.name, type(value), type(alt)))
            yield (setting.name, value)
