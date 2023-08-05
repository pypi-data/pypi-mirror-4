###############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: tests.py 202 2007-03-04 01:03:01Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
