import unittest
from Testing import ZopeTestCase as ztc
from collective.editskinswitcher.tests import base
from collective.editskinswitcher.tests.layer import TestLayer


# There is too much funkyness going on with tests that pass just fine
# when run on their own but fail when combined with the other tests.
# This is probably because we have to do funky stuff in order to test
# changing skins.  So we introduce more test layers so we have more
# isolation.  Funky indeed...

class TestLayer1(TestLayer):
    pass


class FTC1(base.BaseFunctionalTestCase):
    layer = TestLayer1


class TestLayer2(TestLayer):
    pass


class FTC2(base.BaseFunctionalTestCase):
    layer = TestLayer2


class TestLayer3(TestLayer):
    pass


class FTC3(base.BaseFunctionalTestCase):
    layer = TestLayer3


class TestLayer4(TestLayer):
    pass


class FTC4(base.BaseFunctionalTestCase):
    layer = TestLayer4


class TestLayer5(TestLayer):
    pass


class FTC5(base.BaseFunctionalTestCase):
    layer = TestLayer5


def test_suite():
    return unittest.TestSuite([

        # Integration tests that use PloneTestCase and use the
        # functional test browser.
        ztc.ZopeDocFileSuite(
            'tests/force_login.txt',
            package='collective.editskinswitcher',
            test_class=FTC1),

        ztc.ZopeDocFileSuite(
            'tests/ssl_switch.txt',
            package='collective.editskinswitcher',
            test_class=FTC2),

        ztc.ZopeDocFileSuite(
            'tests/need_authentication.txt',
            package='collective.editskinswitcher',
            test_class=FTC3),

        ztc.ZopeDocFileSuite(
            'tests/ploneadmin_header.txt',
            package='collective.editskinswitcher',
            test_class=FTC4),

        ztc.ZopeDocFileSuite(
            'tests/preview.txt',
            package='collective.editskinswitcher',
            test_class=base.PreviewFunctionalTestCase),

        ztc.ZopeDocFileSuite(
            'tests/specific_switch.txt',
            package='collective.editskinswitcher',
            test_class=FTC5),

        ])
