import logging
from Products.PloneTestCase import PloneTestCase as ptc

from ZPublisher import HTTPRequest

from collective.editskinswitcher.tests.layer import PreviewTestLayer
from collective.editskinswitcher.tests.layer import TestLayer
from collective.editskinswitcher.tests.utils import dummy_sunburst_skin
from collective.editskinswitcher.tests.utils import fake_externalEditorEnabled
from collective.editskinswitcher.tests.utils import new_default_skin

logger = logging.getLogger('collective.editskinswitcher')


def get_header(self, name, default=None):
    """Return the named HTTP header, or an optional default
    argument or None if the header is not found. Note that
    both original and CGI-ified header names are recognized,
    e.g. 'Content-Type', 'CONTENT_TYPE' and 'HTTP_CONTENT_TYPE'
    should all return the Content-Type header, if available.

    CHANGED from original:

    For testing, we first try the default behaviour.  When that fails
    we try to get the name from the request variables.  The reason is
    that it is rather hard to mock an extra header like X_FORCE_LOGIN.
    """
    original = self.old_get_header(name, default=default)
    if original is default:
        val = self.get(name, default=default)
        if val is not None:
            return val
    return original


HTTPRequest.HTTPRequest.old_get_header = HTTPRequest.HTTPRequest.get_header
HTTPRequest.HTTPRequest.get_header = get_header
logger.info('Patched ZPublisher.HTTPRequest.HTTPRequest.get_header for tests.')


class BaseTestCase(ptc.PloneTestCase):
    """Base class for test cases.
    """

    layer = TestLayer

    def setUp(self):
        super(BaseTestCase, self).setUp()
        # Add Sunburst skin if it does not exist.
        dummy_sunburst_skin(self.portal)
        # Add fake script to avoid strange problem.
        fake_externalEditorEnabled(self.portal)
        # Create new skin based on Sunburst Theme and make this the
        # default skin.
        new_default_skin(self.portal)


class BaseFunctionalTestCase(ptc.FunctionalTestCase):
    """Base class for test cases.
    """

    layer = TestLayer

    def setUp(self):
        super(BaseFunctionalTestCase, self).setUp()
        # Add Sunburst skin if it does not exist.
        dummy_sunburst_skin(self.portal)
        # Add fake script to avoid strange problem.
        fake_externalEditorEnabled(self.portal)
        # Create new skin based on Sunburst Theme and make this the
        # default skin.
        new_default_skin(self.portal)


class PreviewFunctionalTestCase(ptc.FunctionalTestCase):
    """Class for functional test cases with @@preview.
    """

    layer = PreviewTestLayer

    def setUp(self):
        super(PreviewFunctionalTestCase, self).setUp()
        # Add Sunburst skin if it does not exist.
        dummy_sunburst_skin(self.portal)
        # Add fake script to avoid strange problem.
        fake_externalEditorEnabled(self.portal)
        # Create new skin based on Sunburst Theme and make this the
        # default skin.
        new_default_skin(self.portal)


ptc.setupPloneSite(products=['collective.editskinswitcher'])
