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
__version_info__ = (0, 0, 8)
__build__ = 0x000008
__version__ = ".".join(map(str, __version_info__))
__maintainer__ = "Alexandr Lispython (alex@obout.ru)"

VERSION = __version__
VERSION_INFO = __version_info__


from base import Commandor, Command
import colors

assert Commandor
assert Command
assert colors
