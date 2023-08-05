##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: tests.py 2697 2011-12-03 02:38:57Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import unittest
from zope.testing import doctest
from zope.testing import doctestunit


def test_suite():
    return unittest.TestSuite((
        doctestunit.DocFileSuite('README.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     globs={'pprint': doctestunit.pprint}
                     ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
