"""
*******
Configs
*******

**Configs** is an INI configuration parsing package, written for humans.

Basic usage
===========
Load a config file::

    >>> import configs
    >>> c = configs.load('sample.conf')
    >>> c['general']
    {'foo': 'baz'}

Load a config file with a fallback config file (with default values)::

    >>> fc = configs.load('sample.conf', fallback_file='default.conf')
    >>> fc['general']['spam']
    eggs

See the full documentation at `configs.rtfd.org <http://configs.rtfd.org>`_.

The repo is at `bitbucket.org/moigagoo/configs <https://bitbucket.org/moigagoo/configs>`_.
"""

__title__ = 'configs'
__version__ = '1.8.2'
__author__ = 'Konstantin Molchanov'
__license__ = 'MIT'

from .section import Section
from .config import Config
from .api import load
