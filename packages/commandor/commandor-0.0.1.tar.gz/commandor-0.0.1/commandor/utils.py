#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
commandor.utils
~~~~~~~~~~~~~~~

Commandor helpers

:copyright: (c) 2012 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
:github: http://github.com/Lispython/commandor
"""

__all__ = 'indent',

def indent(s, level=4):
    """Add indentation for string

    :param s: string to indents
    :param level: indentation level
    :return: `s` with `level` indentation
    :rtype: string
    """
    return u" " * level + s
