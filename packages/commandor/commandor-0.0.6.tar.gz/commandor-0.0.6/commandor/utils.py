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

__all__ = 'indent', 'parse_args'


def indent(s, level=4):
    """Add indentation for string

    :param s: string to indents
    :param level: indentation level
    :return: `s` with `level` indentation
    :rtype: string
    """
    return u" " * level + s


def parse_args(args):
    """Separate script and command args

    :param args: script args
    :return: tuple(['script args'],['command', 'names', 'and commands args'])
    """

    index = None

    for i, arg in enumerate(args):
        if not arg.startswith('-'):
            index = i
            break

    if not index:
        return (args, None)

    return (args[:index], args[index:])
