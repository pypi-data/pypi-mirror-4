"""
***********
configs.api
***********

This module implements the configs API.
"""

from .config import Config

def load(config_file, fallback_file=None):
    """Constructs and returns a :class:`Config <Config>` instance.

    :param config_file: configuration file to be parsed
    :param fallback_file: (optional) fallback configuration file with default values to be used if missing in the ``config_file``

    Usage::

        >>> import configs

        >>> fc = configs.load('sample.conf', fallback_file='default.conf')

        >>> fc['general']['spam']
        eggs
    """

    return Config(config_file, fallback_file)
