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

"""The basic h5config classes
"""

import copy as _copy

from . import LOG as _LOG


class Setting (object):
    "A named setting with arbitrary text values."
    def  __init__(self, name, help='', default=None):
        self.name = name
        self._help = help
        self.default = default

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)

    def __repr__(self):
        return self.__str__()

    def help(self):
        ret = '%s  Default: %s.' % (
            self._help, self.convert_to_text(self.default))
        return ret.strip()

    def convert_from_text(self, value):
        return value or None

    def convert_to_text(self, value):
        return value or ''


class ChoiceSetting (Setting):
    """A named setting with a limited number of possible values.

    `choices` should be a list of `(config_file_value, Python value)`
    pairs.  For example

    >>> s = ChoiceSetting(name='bool',
    ...                   choices=[('yes', True), ('no', False)])
    >>> s.convert_from_text('yes')
    True
    >>> s.convert_to_text(True)
    'yes'
    >>> s.convert_to_text('invalid')
    Traceback (most recent call last):
      ...
    ValueError: invalid
    >>> s.help()
    'Default: yes.  Choices: yes, no'
    """
    def __init__(self, choices=None, **kwargs):
        if 'default' not in kwargs:
            if None not in [keyval[1] for keyval in choices]:
                kwargs['default'] = choices[0][1]
        super(ChoiceSetting, self).__init__(**kwargs)
        if choices == None:
            choices = []
        self.choices = choices

    def help(self):
        ret = '%s  Choices: %s' % (
            super(ChoiceSetting, self).help(),
            ', '.join([key for key,value in self.choices]))
        return ret.strip()

    def convert_from_text(self, value):
        return dict(self.choices)[value]

    def convert_to_text(self, value):
        for keyval in self.choices:
            key,val = keyval
            if val == value:
                return key
        raise ValueError(value)


class BooleanSetting (ChoiceSetting):
    """A named settubg that can be either true or false.

    >>> s = BooleanSetting(name='bool')

    >>> s.convert_from_text('yes')
    True
    >>> s.convert_to_text(True)
    'yes'
    >>> s.convert_to_text('invalid')
    Traceback (most recent call last):
      ...
    ValueError: invalid
    >>> s.help()
    'Default: no.  Choices: yes, no'
    """
    def __init__(self, default=False, **kwargs):
        super(BooleanSetting, self).__init__(
            choices=[('yes', True), ('no', False)], default=default, **kwargs)


class NumericSetting (Setting):
    """A named setting with numeric values.

    Don't use this setting class.  Use a more specific subclass, such
    as `IntegerSetting`.

    >>> s = NumericSetting(name='float')
    >>> s.default
    0
    >>> s.convert_to_text(13)
    '13'
    """
    def __init__(self, default=0, **kwargs):
        super(NumericSetting, self).__init__(default=default, **kwargs)

    def convert_to_text(self, value):
        return str(value)

    def convert_from_text(self, value):
        if value in [None, 'None']:
            return None
        return self._convert_from_text(value)

    def _convert_from_text(self, value):
        raise NotImplementedError()


class IntegerSetting (NumericSetting):
    """A named setting with integer values.

    >>> s = IntegerSetting(name='int')
    >>> s.default
    1
    >>> s.convert_from_text('8')
    8
    """
    def __init__(self, default=1, **kwargs):
        super(IntegerSetting, self).__init__(default=default, **kwargs)

    def _convert_from_text(self, value):
        return int(value)


class FloatSetting (NumericSetting):
    """A named setting with floating point values.

    >>> s = FloatSetting(name='float')
    >>> s.default
    1.0
    >>> s.convert_from_text('8')
    8.0
    >>> try:
    ...     s.convert_from_text('invalid')
    ... except ValueError as e:
    ...     print('caught a ValueError')
    caught a ValueError
    """
    def __init__(self, default=1.0, **kwargs):
        super(FloatSetting, self).__init__(default=default, **kwargs)

    def _convert_from_text(self, value):
        return float(value)


class ListSetting(Setting):
    """A named setting with a list of string values.

    >>> s = ListSetting(name='list')
    >>> s.default
    []
    >>> s.convert_to_text(['abc', 'def'])
    'abc,def'
    >>> s.convert_from_text('uvw, xyz')
    ['uvw', ' xyz']
    >>> s.convert_to_text([])
    ''
    >>> s.convert_from_text('')
    []
    """
    def __init__(self, default=None, **kwargs):
        if default is None:
            default = []
        super(ListSetting, self).__init__(default=default, **kwargs)

    def _convert_from_text(self, value):
        return value

    def convert_from_text(self, value):
        if value is None:
            return None
        elif value in ['', []]:
            return []
        return [self._convert_from_text(x) for x in value.split(',')]

    def convert_to_text(self, value):
        if value is None:
            return None
        return ','.join([str(x) for x in value])

class IntegerListSetting (ListSetting):
    """A named setting with a list of integer point values.

    >>> s = IntegerListSetting(name='integerlist')
    >>> s.default
    []
    >>> s.convert_to_text([1, 3])
    '1,3'
    >>> s.convert_from_text('4, -6')
    [4, -6]
    >>> s.convert_to_text([])
    ''
    >>> s.convert_from_text('')
    []
    """
    def _convert_from_text(self, value):
        if value is None:
            return value
        return int(value)


class FloatListSetting (ListSetting):
    """A named setting with a list of floating point values.

    >>> s = FloatListSetting(name='floatlist')
    >>> s.default
    []
    >>> s.convert_to_text([1, 2.3])
    '1,2.3'
    >>> s.convert_from_text('4.5, -6.7')  # doctest: +ELLIPSIS
    [4.5, -6.7...]
    >>> s.convert_to_text([])
    ''
    >>> s.convert_from_text('')
    []
    """
    def _convert_from_text(self, value):
        if value is None:
            return value
        return float(value)


class ConfigSetting (Setting):
    """A setting that holds a pointer to a child `Config` class

    This allows you to nest `Config`\s, which is a useful way to
    contain complexity.  In order to save such a config, the backend
    must be able to handle hierarchical storage (possibly via
    references).

    For example, a configurable AFM may contain a configurable piezo
    scanner, as well as a configurable stepper motor.
    """
    def __init__(self, config_class=None, **kwargs):
        super(ConfigSetting, self).__init__(**kwargs)
        self.config_class = config_class


class ConfigListSetting (ConfigSetting):
    """A setting that holds a list of child `Config` classes

    For example, a piezo scanner with several axes.
    """
    def __init__(self, default=[], **kwargs):
        super(ConfigListSetting, self).__init__(**kwargs)


class Config (dict):
    """A class with a list of `Setting`\s.

    `Config` instances store their values just like dictionaries, but
    the attached list of `Settings`\s allows them to intelligently
    dump, save, and load those values.
    """
    settings = []

    def __init__(self, storage=None):
        super(Config, self).__init__()
        self.clear()
        self.set_storage(storage=storage)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, id(self))

    def set_storage(self, storage):
        self._storage = storage

    def clear(self):
        super(Config, self).clear()
        for s in self.settings:
            # copy to avoid ambiguity with mutable defaults
            self[s.name] = _copy.deepcopy(s.default)

    def load(self, merge=False, **kwargs):
        self._storage.load(config=self, merge=merge, **kwargs)

    def save(self, merge=False, **kwargs):
        self._storage.save(config=self, merge=merge, **kwargs)

    def dump(self, help=False, prefix=''):
        """Return all settings and their values as a string

        >>> class MyConfig (Config):
        ...     settings = [
        ...         ChoiceSetting(
        ...             name='number',
        ...             help='I have a number behind my back...',
        ...             default=1,
        ...             choices=[('one', 1), ('two', 2),
        ...                 ]),
        ...         BooleanSetting(
        ...             name='odd',
        ...             help='The number behind my back is odd.',
        ...             default=True),
        ...         IntegerSetting(
        ...             name='guesses',
        ...             help='Number of guesses before epic failure.',
        ...             default=2),
        ...         ]
        >>> c = MyConfig()
        >>> print(c.dump())
        number: one
        odd: yes
        guesses: 2
        >>> print(c.dump(help=True))  # doctest: +NORMALIZE_WHITESPACE
        number: one (I have a number behind my back...  Default: one.
                     Choices: one, two)
        odd: yes    (The number behind my back is odd.  Default: yes.
                     Choices: yes, no)
        guesses: 2  (Number of guesses before epic failure.  Default: 2.)
        """
        lines = []
        for setting in self.settings:
            name = setting.name
            value = self[name]
            try:
                if isinstance(setting, ConfigListSetting):
                    if value:
                        lines.append('{}{}:'.format(prefix, name))
                        for i,config in enumerate(value):
                            lines.append('{}  {}:'.format(prefix, i))
                            lines.append(
                                config.dump(help=help, prefix=prefix+'    '))
                        continue
                elif isinstance(setting, ConfigSetting):
                    if value is not None:
                        lines.append('{}{}:'.format(prefix, name))
                        lines.append(value.dump(help=help, prefix=prefix+'  '))
                        continue
                value_string = setting.convert_to_text(self[name])
                if help:
                    help_string = '\t({})'.format(setting.help())
                else:
                    help_string = ''
                lines.append('{}{}: {}{}'.format(
                        prefix, name, value_string, help_string))
            except Exception:
                _LOG.error('could not dump {} ({!r})'.format(name, value))
                raise
        return '\n'.join(lines)

    def select_config(self, setting_name, attribute_value=None,
                      get_attribute=lambda value : value['name']):
        """Select a `Config` instance from `ConfigListSetting` values

        If your don't want to select `ConfigListSetting` items by
        index, you can select them by matching another attribute.  For
        example:

        >>> from .test import TestConfig
        >>> c = TestConfig()
        >>> c['children'] = []
        >>> for name in ['Jack', 'Jill']:
        ...     child = TestConfig()
        ...     child['name'] = name
        ...     c['children'].append(child)
        >>> child = c.select_config('children', 'Jack')
        >>> child  # doctest: +ELLIPSIS
        <TestConfig ...>
        >>> child['name']
        'Jack'

        `get_attribute` defaults to returning `value['name']`, because
        I expect that to be the most common case, but you can use
        another function if neccessary, for example to drill down more
        than one level.  Here we select by grandchild name:

        >>> for name in ['Jack', 'Jill']:
        ...     grandchild = TestConfig()
        ...     grandchild['name'] = name + ' Junior'
        ...     child = c.select_config('children', name)
        ...     child['children'] = [grandchild]
        >>> get_grandchild = lambda value : value['children'][0]['name']
        >>> get_grandchild(child)
        'Jill Junior'
        >>> child = c.select_config('children', 'Jack Junior',
        ...     get_attribute=get_grandchild)
        >>> child  # doctest: +ELLIPSIS
        <TestConfig ...>
        >>> child['name']
        'Jack'
        """
        setting_value = self.get(setting_name, None)
        if not setting_value:
            raise KeyError(setting_name)
        for item in setting_value:
            if get_attribute(item) == attribute_value:
                return item
        raise KeyError(attribute_value)
