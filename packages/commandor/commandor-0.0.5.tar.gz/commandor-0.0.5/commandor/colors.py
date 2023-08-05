#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
commandor.colors
~~~~~~~~~~~~~~~

ANSI colors for console

:copyright: (c) 2012 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
:github: http:/github.com/Lispython/commandor
"""

def colorize(code):
    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;{0}".format(c)
        return "\033[{code}m{text}\033[0m".format(code=c, text=text)
    return inner


red = colorize('31')
green = colorize('32')
yellow = colorize('33')
blue = colorize('34')
magenta = colorize('35')
cyan = colorize('36')
white = colorize('37')
