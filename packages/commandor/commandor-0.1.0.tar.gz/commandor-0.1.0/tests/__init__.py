#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
commandor.tests
~~~~~~~~~~~~~~~

tests

:copyright: (c) 2012 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
:github: http://github.com/Lispython/commandor
"""

import unittest

from core import CoreTestCase


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CoreTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest="suite")
