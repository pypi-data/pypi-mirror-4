import unittest
import doctest
from Testing import ZopeTestCase as ztc
from collective.sharerizer.tests import base


def test_suite():
    return unittest.TestSuite([

        # Demonstrate the main content types
        ztc.FunctionalDocFileSuite(
            'doctests.txt', package='collective.sharerizer.tests',
            test_class=base.FunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
