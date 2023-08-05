#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
commandor.tests.cookbooks
~~~~~~~~~~~~~~~~~~~~~~~~

Test cookbooks module

:copyright: (c) 2012 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
:github: http://github.com/Lispython/commandor
"""

import os.path
import unittest
import logging

__all__ = 'BaseTestCase',

logger = logging.getLogger("commandor.test")


class BaseTestCase(unittest.TestCase):
    """Base test case
    """
    def setUp(self):
        self.logger = logger

    def tearDown(self):
        super(BaseTestCase, self).tearDown()

    @staticmethod
    def rel(*parts):
        return os.path.join(*parts)
