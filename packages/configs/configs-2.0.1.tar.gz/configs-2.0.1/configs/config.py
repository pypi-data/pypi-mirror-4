"""
**************
configs.config
**************

This module contains the :class:`Config <Config>` class.
"""

import re

from .section import Section

class Config:
    """Parsed configuration.

    Config instance includes a list of :class:`Section <Section>` instances.
    """

    _comment = re.compile('^\s*;.*$')
    _header = re.compile('^\s*\[\s*(?P<section>\w+)\s*\]\s*$')
    _dict_item = re.compile('^\s*(?P<key>\w+)\s*\=\s*(?P<value>.+)\s*$')
    _list_item = re.compile('^\s*(?P<value>.+)\s*$')

    def __init__(self, config_file=None, fallback=None):
        if fallback:
            self.sections = fallback.sections
        else:
            self.sections = {}
            self._add_section('root')

        if config_file:
            self.load(config_file)
            self.config_file = config_file
        else:
            self.config_file = fallback.config_file

    def get(self):
        """Gets all section items."""

        return {section: self.sections[section].get() for section in self.sections}

    def load(self, config_file):
        """Parse an INI configuration file.

        :param config_file: configuration file to be loaded.

        :returns: :class:Config instance.
        """

        current_section = None

        with open(config_file) as f:
            for line in f.readlines():
                comment_match = re.match(self._comment, line)
                if comment_match:
                    continue

                header_match = re.match(self._header, line)
                if header_match:
                    current_section = header_match.group('section')
                    if not current_section in self.sections:
                        self._add_section(current_section)

                    continue

                dict_item_match = re.match(self._dict_item, line)
                if dict_item_match:
                    key, value = dict_item_match.group('key'), dict_item_match.group('value')

                    if current_section:
                        self._add_dict_prop_to_section(key, value, current_section)
                    else:
                        self._add_dict_prop_to_section(key, value)

                    continue

                list_item_match = re.match(self._list_item, line)
                if list_item_match:
                    value = list_item_match.group('value')
                    if current_section:
                        self._add_list_prop_to_section(value, current_section)
                    else:
                        self._add_list_prop_to_section(value)

                    continue

    def _add_section(self, name):
        """Adds an empty section with the given name.

        :param name: new section name.
        """

        self.sections[name] = Section()

    def _add_dict_prop_to_section(self, key, value, section='root'):
        """Adds a key-value item to the given section.

        :param key: new item key.
        :param value: new item value.
        :param section: (optional) section name (``root`` by default).
        """

        if section in self.sections:
            self.sections[section]._add_dict_prop(key, value)
        else:
            raise KeyError

    def _add_list_prop_to_section(self, value, section='root'):
        """Adds a flag value to the given section.

        :param value: new item value.
        :param section: (optional) section name (``root`` by default).
        """

        if section in self.sections:
            self.sections[section]._add_list_prop(value)
        else:
            raise KeyError

    def __repr__(self):
        return str(self.get())

    def __str__(self):
        return str(self.get())

    def __getitem__(self, key):
        if key in self.sections:
            return self.sections[key]
        else:
            try:
                return self.sections['root'][key]
            except KeyError:
                pass

        return None

    def __eq__(self, other):
        return self.sections == other.sections
