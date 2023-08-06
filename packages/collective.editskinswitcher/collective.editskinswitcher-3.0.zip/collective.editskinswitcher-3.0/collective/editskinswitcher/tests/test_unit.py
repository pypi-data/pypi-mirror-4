import unittest
import doctest
from zope.component import testing


def test_suite():
    return unittest.TestSuite([
        doctest.DocTestSuite(
            module='collective.editskinswitcher.utils',
            setUp=testing.setUp, tearDown=testing.tearDown),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
