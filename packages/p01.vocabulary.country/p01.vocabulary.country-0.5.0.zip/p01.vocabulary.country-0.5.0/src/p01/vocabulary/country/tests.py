##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: tests.py 27 2007-01-28 06:02:30Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import unittest
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.testing.doctestunit import pprint


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            globs={'pprint': pprint}
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
