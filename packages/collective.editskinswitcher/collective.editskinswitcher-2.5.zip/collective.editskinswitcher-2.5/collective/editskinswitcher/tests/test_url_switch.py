import unittest
from Testing import ZopeTestCase as ztc
from base import BaseTestCase


def test_suite():
    return unittest.TestSuite([

        # Integration tests that use PloneTestCase but no functional
        # test browser.
        ztc.ZopeDocFileSuite(
            'url_switch.txt', package='collective.editskinswitcher.tests',
            test_class=BaseTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
