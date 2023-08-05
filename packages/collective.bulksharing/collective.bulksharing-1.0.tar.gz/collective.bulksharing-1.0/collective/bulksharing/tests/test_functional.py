import doctest
from unittest import TestSuite

from Testing.ZopeTestCase import FunctionalDocFileSuite
from collective.bulksharing.tests.base import BulkSharingFunctionalTestCase

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


def test_suite():
    suite = TestSuite()
    suite.addTest(FunctionalDocFileSuite('bulksharing_view.txt',
                                      optionflags=optionflags,
                                      package="collective.bulksharing.tests",
                                      test_class=BulkSharingFunctionalTestCase))
    return suite
