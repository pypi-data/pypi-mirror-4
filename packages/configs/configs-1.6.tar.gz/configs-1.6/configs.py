#!/usr/bin/env python

import re


class Section:
    """INI configuration section

    A Section instance stores both key-value and flag items, in ``dict_props`` and ``list_props`` attributes respectively.

    It is possible to iterate over a section; flag values are listed first, then key-value items.

    """
    def __init__(self):
        self.dict_props = {}
        self.list_props = []

    def get(self):
        """Gets section values.

        If section contains only flag values, a list is returned.

        If section contains only key-value items, a dictionary is returned.

        If section contains both flag and key-value items, a tuple of both is returned.
        """
        if self.list_props and self.dict_props:
            return self.list_props, self.dict_props

        return self.list_props or self.dict_props or None

    def _add_dict_prop(self, key, value):
        """Adds a key-value item to section."""

        try:
            value = float(value)
            value = int(value)
        except ValueError:
            pass

        self.dict_props[key] = value

    def _add_list_prop(self, value):
        """Adds a flag value to  section."""

        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass

        self.list_props.append(value)

    def __repr__(self):
        return str(self.get())

    def __str__(self):
        return str(self.get())

    def __iter__(self):
        for list_prop in self.list_props:
            yield list_prop

        for dict_prop in self.dict_props:
            yield dict_prop

    def __getitem__(self, key):
        try:
            return self.dict_props[key]
        except KeyError:
            pass

        try:
            return self.list_props[key]
        except (KeyError, TypeError):
            pass

        return None

    def __eq__(self, other):
        return self.dict_props == other.dict_props and self.list_props == other.list_props

class Config:
    """Parsed configuration.

    Config consists of Sections.
    """

    #Regexes for INI header, key-value, and flag item parsing
    comment = re.compile('^\s*;.*$')
    header = re.compile('^\s*\[\s*(?P<section>\w+)\s*\]\s*$')
    dict_item = re.compile('^\s*(?P<key>\w+)\s*\=\s*(?P<value>.+)\s*$')
    list_item = re.compile('^\s*(?P<value>.+)\s*$')

    def __init__(self, config_file=None, fallback=None):
        if fallback:
            self.sections = fallback.sections
        else:
            self.sections = {}
            self._add_section('root')

        if config_file:
            self.load(config_file)

    def get(self):
        """Gets all section items."""

        return {section: self.sections[section].get() for section in self.sections}

    def load(self, config_file):
        """Parse an INI configuration file.

        :returns: Config instance.
        """

        current_section = None

        with open(config_file, 'r') as f:
            for line in f.readlines():
                comment_match = re.match(self.comment, line)
                if comment_match:
                    continue

                header_match = re.match(self.header, line)
                if header_match:
                    current_section = header_match.group('section')
                    #if not current_section in self.sections:
                    self._add_section(current_section)

                    continue

                dict_item_match = re.match(self.dict_item, line)
                if dict_item_match:
                    key, value = dict_item_match.group('key'), dict_item_match.group('value')

                    if current_section:
                        self._add_dict_prop_to_section(key, value, current_section)
                    else:
                        self._add_dict_prop_to_section(key, value)

                    continue

                list_item_match = re.match(self.list_item, line)
                if list_item_match:
                    value = list_item_match.group('value')
                    if current_section:
                        self._add_list_prop_to_section(value, current_section)
                    else:
                        self._add_list_prop_to_section(value)

                    continue

    def _add_section(self, name):
        """Adds an empty section with the given name."""

        self.sections[name] = Section()

    def _add_dict_prop_to_section(self, key, value, section='root'):
        """Adds a key-value item to the given section."""

        if section in self.sections:
            self.sections[section]._add_dict_prop(key, value)
        else:
            raise KeyError

    def _add_list_prop_to_section(self, value, section='root'):
        """Adds a flag value to the given section."""

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


def load(config_file, fallback_file=None):
    if fallback_file:
        return Config(config_file, Config(fallback_file))
    else:
        return Config(config_file)

if __name__ == '__main__':
    config_w_fallback = load('test.conf', fallback_file='fallback.conf')
    print('test.conf used with fallback.conf as fallback:\n', config_w_fallback)

    config_wo_fallback= load('test.conf')
    print('test.conf used without fallback:\n', config_wo_fallback)
