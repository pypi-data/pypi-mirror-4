from zope.publisher.browser import TestRequest as baseTestRequest
from Products.CMFCore.exportimport.skins import importSkinsTool
from Products.GenericSetup.tests.common import DummyImportContext

SKINCONFIG = """\
<?xml version="1.0"?>
<!-- This file adds in the Monty Python test skins layer with a test template
  -->

<object name="portal_skins"
  allow_any="False"
  cookie_persistence="False"
  default_skin="Monty Python Skin">

 <object name="editskinswitcher_tests"
    meta_type="Filesystem Directory View"
    directory="collective.editskinswitcher:tests/skins/editskinswitcher_tests"
    />

 <skin-path name="Monty Python Skin" based-on="Sunburst Theme">
  <layer name="editskinswitcher_tests"
     insert-after="custom"/>
 </skin-path>

</object>
"""

DUMMY_SUNBURST_SKINCONFIG = """\
<?xml version="1.0"?>
<!-- This file adds a dummy Sunburst Theme when on Plone 3. -->

<object name="portal_skins"
  default_skin="Sunburst Theme">

 <skin-path name="Sunburst Theme" based-on="Plone Default" />
</object>
"""


def _hold(self, object):
    """Hold a reference to an object to delay it's destruction until mine

    Taken from ZPublisher/BaseRequest.py
    Needed by CMFCore/Skinnable.py(142)changeSkin()
    """
    if self._held is not None:
        self._held = self._held + (object, )


class TestRequest(baseTestRequest):
    """ This just adds the set, get methods of the real REQUEST object """

    def set(self, key, value):
        self.form[key] = value

    def get_header(self, *args, **kwargs):
        """Get something from the header.

        This method is not available on a base test request, but we
        need it for some checks.
        """
        return self.get(*args, **kwargs)

TestRequest._hold = _hold


def new_default_skin(portal):
    """ Register test skins folder with extra test template - zcml
        then make new default skin based on Sunburst Theme with test skin - xml
    """
    importcontext = DummyImportContext(portal, False)
    importcontext._files['skins.xml'] = SKINCONFIG
    importSkinsTool(importcontext)


def dummy_sunburst_skin(portal):
    """ Register dummy Sunburst Theme skin selection based on Plon Default.

    Only needed to make the tests compatible with Plone 3, which does
    not have the Sunburst Theme.
    """
    if 'Sunburst Theme' in portal.portal_skins.getSkinSelections():
        return
    importcontext = DummyImportContext(portal, False)
    importcontext._files['skins.xml'] = DUMMY_SUNBURST_SKINCONFIG
    importSkinsTool(importcontext)


def fake_externalEditorEnabled(portal):
    # Add a dummy replacement for the externalEditorEnabled.py
    # python skin script, which is somehow missing when running the
    # tests with Plone 3.  Or Plone 4.0 for that matter, and maybe
    # simply always.
    portal.externalEditorEnabled = False


class FakeTraversalEvent(object):

    def __init__(self, object, request):
        self.object = object
        self.request = request


def clear_log_entries(portal):
    for entry in portal.error_log.getLogEntries():
        portal.error_log.forgetEntry(entry['id'])


def print_latest_log_entry(portal, clear=True):
    if portal.error_log.getLogEntries():
        print portal.error_log.getLogEntries()[-1]['tb_text']
        clear_log_entries(portal)


def changeSkin(context, name, request=None):
    # Our own version of changeSkin, which only changes something when
    # the skin is not yet the current skin.  This hopefully avoids
    # some test failures.  Well, it does not... :-/
    if context.getCurrentSkinName() == name:
        return
    if request is None:
        request = TestRequest()
    context.changeSkin(name, request)
