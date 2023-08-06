"""
***************
configs.section
***************

This module contains the :class:`Section <Section>` class.
"""

class Section:
    """INI configuration section.

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

        if value == 'True':
            value = True
        elif value == 'False':
            value = False
        else:
            try:
                value = float(value)
                value = int(value)
            except ValueError:
                pass

        self.dict_props[key] = value

    def _add_list_prop(self, value):
        """Adds a flag value to  section."""

        if value == 'True':
            value = True
        elif value == 'False':
            value = False
        else:
            try:
                value = float(value)
                value = int(value)
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
