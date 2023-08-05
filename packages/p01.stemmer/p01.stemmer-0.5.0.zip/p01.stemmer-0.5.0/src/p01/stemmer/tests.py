##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
##############################################################################
"""tests
$Id: tests.py 3473 2012-11-22 13:54:35Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            encoding='utf-8'),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
