#!/usr/bin/env python

import re

#Regexs for INI header, key-value, and flag item parsing
header = re.compile('^\s*\[\s*(?P<section>\w+)\s*\]\s*$')
dict_item = re.compile('^\s*(?P<key>\w+)\s*\=\s*(?P<value>[\S]+)\s*$')
list_item = re.compile('^\s*(?P<value>[\S]+)\s*$')

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
            yield self.dict_props[dict_prop]

    def __getitem__(self, key):
        try:
            return self.dict_props[key]
        except KeyError:
            pass

        try:
            return self.list_props[key]
        except (KeyError, TypeError):
            pass

        raise KeyError


class Config:
    """Parsed configuration.

    Config consists of Sections.
    """
    def __init__(self):
        self.sections = {}

        self._add_section('root')

    def get(self):
        """Gets all section items."""

        return {section: self.sections[section].get() for section in self.sections}

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

        raise KeyError


def load(config_file):
    """Parse an INI configuration file.

    :returns: Config instance.
    """

    config = Config()

    current_section = None

    with open(config_file, 'r') as f:
        for line in f.readlines():
            header_match = re.match(header, line)
            if header_match:
                current_section = header_match.group('section')
                if not current_section in config:
                    config._add_section(current_section)

                continue

            dict_item_match = re.match(dict_item, line)
            if dict_item_match:
                key, value = dict_item_match.group('key'), dict_item_match.group('value')

                if current_section:
                    config._add_dict_prop_to_section(key, value, current_section)
                else:
                    config._add_dict_prop_to_section(key, value)

                continue

            list_item_match = re.match(list_item, line)
            if list_item_match:
                value = list_item_match.group('value')
                if current_section:
                    config._add_list_prop_to_section(value, current_section)
                else:
                    config._add_list_prop_to_section(value)

                continue

    return config


if __name__ == '__main__':
    config = load('sample.conf')
    print(config)
