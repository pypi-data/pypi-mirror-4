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

import os.path as _os_path
import sys as _sys

import h5py as _h5py
import numpy as _numpy

from .. import LOG as _LOG
from .. import config as _config
from . import FileStorage as _FileStorage
from . import is_string as _is_string


def pprint_HDF5(*args, **kwargs):
    print(pformat_HDF5(*args, **kwargs))

def pformat_HDF5(filename, group='/'):
    try:
        with _h5py.File(filename, 'r') as f:
            cwg = f[group]
            ret = '\n'.join(_pformat_hdf5(cwg))
    except IOError as e:
        if 'unable to open' in e.message:
            if _os_path.getsize(filename) == 0:
                return 'EMPTY'
            return None
        raise
    return ret

def _pformat_hdf5(cwg, depth=0):
    lines = []
    lines.append('  '*depth + cwg.name)
    depth += 1
    for key,value in cwg.items():
        if isinstance(value, _h5py.Group):
            lines.extend(_pformat_hdf5(value, depth))
        elif isinstance(value, _h5py.Dataset):
            lines.append('  '*depth + str(value))
            lines.append('  '*(depth+1) + str(value[...]))
        else:
            lines.append('  '*depth + str(value))
    return lines

def h5_create_group(cwg, path, force=False):
    "Create the group where the settings are stored (if necessary)."
    if path == '/':
        return cwg
    gpath = ['']
    for group in path.strip('/').split('/'):
        gpath.append(group)
        if group not in cwg.keys():
            _LOG.debug('creating group {} in {}'.format(
                    '/'.join(gpath), cwg.file))
            cwg.create_group(group)
        _cwg = cwg[group]
        if isinstance(_cwg, _h5py.Dataset):
            if force:
                _LOG.info('overwrite {} in {} ({}) with a group'.format(
                        '/'.join(gpath), _cwg.file, _cwg))
                del cwg[group]
                _cwg = cwg.create_group(group)
            else:
                raise ValueError(_cwg)
        cwg = _cwg
    return cwg


class HDF5_Storage (_FileStorage):
    """Back a `Config` class with an HDF5 file.

    The `.save` and `.load` methods have an optional `group` argument
    that allows you to save and load settings from an externally
    opened HDF5 file.  This can make it easier to stash several
    related `Config` classes in a single file.  For example

    >>> import os
    >>> import tempfile
    >>> from ..test import TestConfig
    >>> fd,filename = tempfile.mkstemp(
    ...     suffix='.'+HDF5_Storage.extension, prefix='pypiezo-')
    >>> os.close(fd)

    >>> f = _h5py.File(filename, 'a')
    >>> c = TestConfig(storage=HDF5_Storage(
    ...     filename='untouched_file.h5', group='/untouched/group'))
    >>> c['alive'] = True
    >>> group = f.create_group('base')
    >>> c.save(group=group)
    >>> pprint_HDF5(filename)  # doctest: +REPORT_UDIFF, +ELLIPSIS
    /
      /base
        <HDF5 dataset "age": shape (), type "<f8">
          1.3
        <HDF5 dataset "alive": shape (), type "|b1">
          True
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
    >>> c.clear()
    >>> c['alive']
    False
    >>> c.load(group=group)
    >>> c['alive']
    True

    >>> f.close()
    >>> os.remove(filename)
    """
    extension = 'h5'

    def __init__(self, group='/', **kwargs):
        super(HDF5_Storage, self).__init__(**kwargs)
        if isinstance(group, _h5py.Group):
            self._file_checked = True
        else:
            assert group.startswith('/'), group
            if not group.endswith('/'):
                group += '/'
            self._file_checked = False
        self.group = group

    def _check_file(self):
        if self._file_checked:
            return
        self._setup_file()
        self._file_checked = True

    def _setup_file(self):
        self._create_basedir(filename=self._filename)
        with _h5py.File(self._filename, 'a') as f:
            cwg = f  # current working group
            h5_create_group(cwg, self.group)

    def _load(self, config, group=None):
        f = None
        try:
            if group is None:
                if isinstance(self.group, _h5py.Group):
                    group = self.group
                else:
                    self._check_file()
                    f = _h5py.File(self._filename, 'r')
                    group = f[self.group]
            for s in config.settings:
                if s.name not in group.keys():
                    continue
                if isinstance(s, _config.ConfigListSetting):
                    try:
                        cwg = h5_create_group(group, s.name)
                    except ValueError:
                        pass
                    else:
                        value = []
                        for i in sorted(int(x) for x in cwg.keys()):
                            instance = s.config_class()
                            try:
                                _cwg = h5_create_group(cwg, str(i))
                            except ValueError:
                                pass
                            else:
                                self._load(config=instance, group=_cwg)
                                value.append(instance)
                        config[s.name] = value
                elif isinstance(s, _config.ConfigSetting):
                    try:
                        cwg = h5_create_group(group, s.name)
                    except ValueError:
                        pass
                    else:
                        if not config[s.name]:
                            config[s.name] = s.config_class()
                        self._load(config=config[s.name], group=cwg)
                else:
                    try:
                        v = group[s.name][...]
                    except Exception as e:
                        _LOG.error('Could not access {}/{}: {}'.format(
                                group.name, s.name, e))
                        raise 
                    if isinstance(v, _numpy.ndarray):
                        if isinstance(s, _config.BooleanSetting):
                            v = bool(v)  # array(True, dtype=bool) -> True
                        elif v.dtype.type in [_numpy.string_, _numpy.object_]:
                            if isinstance(s, _config.ListSetting):
                                try:
                                    v = list(v)
                                except TypeError:
                                    v = []
                                if _sys.version_info >= (3,):
                                    for i,v_ in enumerate(v):
                                        if isinstance(v_, bytes):
                                            v[i] = str(v_, 'utf-8')
                            else:  # array('abc', dtype='|S3') -> 'abc'
                                if not v.shape:
                                    # array('abc', dtype=object) -> 'abc'
                                    # convert from numpy 0d array
                                    v = v.item()
                                if _sys.version_info >= (3,):
                                    v = str(v, 'utf-8')
                                else:
                                    v = str(v)
                        elif isinstance(s, _config.IntegerSetting):
                            v = int(v)  # array(3, dtpe='int32') -> 3
                        elif isinstance(s, _config.FloatSetting):
                            v = float(v)  # array(1.2, dtype='float64') -> 1.2
                        elif isinstance(s, _config.NumericSetting):
                            raise NotImplementedError(type(s))
                        elif isinstance(s, _config.ListSetting):
                            # convert from numpy array
                            if isinstance(s, _config.IntegerListSetting):
                                conv = int
                            elif isinstance(s, _config.FloatListSetting):
                                conv = float
                            v = list(conv(x) for x in v)
                    if _is_string(v):
                        # convert back from None, etc.
                        v = s.convert_from_text(v)
                    config[s.name] = v
        finally:
            if f:
                f.close()

    def _save(self, config, group=None):
        f = None
        try:
            if group is None:
                if isinstance(self.group, _h5py.Group):
                    group = self.group
                else:
                    self._check_file()
                    f = _h5py.File(self._filename, 'a')
                    group = f[self.group]
            for s in config.settings:
                value = None
                if isinstance(s, (_config.BooleanSetting,
                                  _config.NumericSetting,
                                  _config.ListSetting)):
                    value = config[s.name]
                    if value in [None, []]:
                        value = s.convert_to_text(value)
                elif isinstance(s, _config.ConfigListSetting):
                    configs = config[s.name]
                    if configs:
                        cwg = h5_create_group(group, s.name, force=True)
                        for i,cfg in enumerate(configs):
                            _cwg = h5_create_group(cwg, str(i), force=True)
                            self._save(config=cfg, group=_cwg)
                        continue
                elif isinstance(s, _config.ConfigSetting):
                    cfg = config[s.name]
                    if cfg:
                        cwg = h5_create_group(group, s.name, force=True)
                        self._save(config=cfg, group=cwg)
                        continue
                if value is None:  # not set yet, or invalid
                    value = s.convert_to_text(config[s.name])
                if _sys.version_info >= (3,):  # convert strings to bytes/
                    if isinstance(value, str):
                        value = value.encode('utf-8')
                    elif isinstance(value, list):
                        value = list(value)  # shallow copy
                        for i,v in enumerate(value):
                            if isinstance(v, str):
                                value[i] = v.encode('utf-8')
                try:
                    del group[s.name]
                except KeyError:
                    pass
                try:
                    group[s.name] = value
                except TypeError:
                    raise ValueError((value, type(value)))
        finally:
            if f:
                f.close()
