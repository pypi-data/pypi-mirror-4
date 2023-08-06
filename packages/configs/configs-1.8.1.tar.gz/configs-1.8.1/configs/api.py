"""
***********
configs.api
***********

This module implements the configs API.
"""

from .config import Config

def load(config_file, fallback_file=None):
    """Constructs are returns a :class:`Config <Config>` instance.

    :param config_file: configuration file to be parsed
    :param fallback_file: (optional) fallback configuration file with default values to be used if missing in the ``config_file``

    Usage::

        >>> import configs

        >>> fc = configs.load('sample.conf', fallback_file='default.conf')

        >>> fc['general']['spam']
        eggs
    """

    if fallback_file:
        return Config(config_file, Config(fallback_file))
    else:
        return Config(config_file)

