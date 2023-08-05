import unittest
import doctest

from Testing import ZopeTestCase as ztc
from Products.cron4plone.tests import base


optionflags = (doctest.REPORT_ONLY_FIRST_FAILURE |
              doctest.NORMALIZE_WHITESPACE |
              doctest.ELLIPSIS)


def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(ztc.FunctionalDocFileSuite(
        'tests/cron4plone.txt',
        package='Products.cron4plone',
        test_class=base.cron4ploneTestCase,
        optionflags=optionflags))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
