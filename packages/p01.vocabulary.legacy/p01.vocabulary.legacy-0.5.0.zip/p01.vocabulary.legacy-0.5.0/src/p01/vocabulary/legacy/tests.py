##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: country.py 39 2007-01-28 07:08:55Z roger.ineichen $
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
