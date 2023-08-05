# -*- coding: utf-8 -*-
"""Pyrseas functional tests"""

import unittest

from tests.functional import test_autodoc


def suite():
    tests = unittest.TestSuite()
    tests.addTest(test_autodoc.suite())
    return tests

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
