#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
Commandor
~~~~~~~~~

Python script options and args parser

:copyright: (c) 2012 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
:github: http://github.com/Lispython/commandor
"""


__all__ = 'VERSION', 'VERSION_INFO',\
          'Commandor', 'Command'


__author__ = "Alex Lispython (alex@obout.ru)"
__license__ = "BSD, see LICENSE for more details"
__build__ = 0x000014
__maintainer__ = "Alexandr Lispython (alex@obout.ru)"

try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('commandor').version
except Exception:
    __version__ = 'unknown'

if __version__ == 'unknown':
    __version_info__ = (0, 0, 0)
else:
    __version_info__ = __version__.split('.')

VERSION = __version__
VERSION_INFO = __version_info__


from commandor.base import Commandor, Command
from commandor import colors

