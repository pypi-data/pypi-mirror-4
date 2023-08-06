import unittest
import doctest
from Testing import ZopeTestCase as ztc

from quintagroup.portlet.static.tests.base import FunctionalTestCase

def test_suite():
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            'configlet.txt', package='quintagroup.portlet.static',
            test_class=FunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

     ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')