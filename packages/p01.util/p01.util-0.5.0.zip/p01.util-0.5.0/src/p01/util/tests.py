###############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: tests.py 593 2007-09-01 03:41:19Z roger.ineichen $
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
