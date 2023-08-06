from Products.PloneTestCase import PloneTestCase as ptc
ptc.setupPloneSite()

from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.i18n import translate

from collective.editskinswitcher.browser.interfaces import ISkinsMenu
from collective.editskinswitcher.skin import (
    ANNOTATION_KEY, get_selected_default_skin, set_selected_default_skin)
from collective.editskinswitcher.tests.utils import (
    FakeTraversalEvent, TestRequest, new_default_skin)
from collective.editskinswitcher.traversal import switch_skin
from collective.editskinswitcher.permissions import SetDefaultSkin

from Acquisition import aq_base
from ZPublisher.BeforeTraverse import queryBeforeTraverse

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString
from Products.Five.component import LocalSiteHook, HOOK_NAME
try:
    from Testing.testbrowser import Browser
    Browser  # pyflakes
except ImportError:
    from Products.Five.testbrowser import Browser
from Products.SiteAccess.AccessRule import AccessRule

try:
    # Try import that works in Zope 2.13 or higher first
    from zope.browsermenu.interfaces import IBrowserMenu
    IBrowserMenu  # pyflakes
except ImportError:
    # BBB for Zope 2.12 or lower
    from zope.app.publisher.interfaces.browser import IBrowserMenu

from collective.editskinswitcher.tests import base


class TestContentMenu(base.BaseTestCase):

    def afterSetUp(self):
        self.menu = getUtility(
            IBrowserMenu, name="plone_contentmenu", context=self.folder)
        self.request = self.app.REQUEST

    # Skins sub-menu
    def testSkinsSubMenuIncludedForFolder(self):
        items = self.menu.getMenuItems(self.folder, self.request)
        skinsMenuItem = [
            i for i in items if
            i["extra"]["id"] == "collective-editskinswitcher-menu-skins"][0]
        self.assertEqual(skinsMenuItem["action"],
                         self.folder.absolute_url() + "/select_skin")
        self.failUnless(len(skinsMenuItem["submenu"]) > 0)

    def testSkinsSubMenuNotIncludedForDocument(self):
        self.folder.invokeFactory("Document", "doc")
        items = self.menu.getMenuItems(self.folder.doc, self.request)
        skinsMenuItem = [
            i for i in items if
            i["extra"]["id"] == "collective-editskinswitcher-menu-skins"]
        self.failIf(len(skinsMenuItem) > 0)

    def testSkinsSubMenuNotIncludedWithoutPermission(self):
        # The skins menu is only available for someone that has the
        # 'Set default skin' permission in the folder.
        items = self.menu.getMenuItems(self.folder, self.request)
        skinsMenuItem = [
            i for i in items if
            i["extra"]["id"] == "collective-editskinswitcher-menu-skins"]
        self.failUnless(len(skinsMenuItem) > 0)
        self.folder.manage_permission(
            SetDefaultSkin, ["Manager"], acquire=0, REQUEST=None)
        items = self.menu.getMenuItems(self.folder, self.request)
        skinsMenuItem = [
            i for i in items if
            i["extra"]["id"] == "collective-editskinswitcher-menu-skins"]
        self.failIf(len(skinsMenuItem) > 0)


class TestSkinsMenu(base.BaseTestCase):

    def afterSetUp(self):
        self.menu = getUtility(
            IBrowserMenu, name="collective-editskinswitcher-menu-skins",
            context=self.folder)
        self.request = self.app.REQUEST

    def testSkinsMenuImplementsIBrowserMenu(self):
        self.failUnless(IBrowserMenu.providedBy(self.menu))

    def testSkinsMenuImplementsISkinsMenu(self):
        self.failUnless(ISkinsMenu.providedBy(self.menu))

    def testSkinsMenuFindsSkins(self):
        st = getToolByName(self.folder, "portal_skins")
        skins = st.getSkinSelections()
        actions = self.menu.getMenuItems(self.folder, self.request)
        self.assertEqual(set(skins),
                         set([a["title"] for a in actions]))
        description = translate(actions[0]["description"])
        self.assertEqual(u"Use '%s' skin for this folder" % actions[0]["title"],
                         description)
        param = "switchDefaultSkin?skin_name=%s" % actions[0]["title"]
        self.assertEqual(param, actions[0]["action"].split("@@")[1])
        skin_id = normalizeString(actions[0]["title"], "utf-8")
        self.assertEqual("collective.editskinswitcher-skin-%s" % skin_id,
                         actions[0]["extra"]["id"])

    def testSelectedSkinHasProperCSSClass(self):
        st = getToolByName(self.folder, "portal_skins")
        skins = st.getSkinSelections()
        actions = self.menu.getMenuItems(self.folder, self.request)
        action = [a for a in actions if a["title"] == skins[0]][0]
        self.assertEqual("actionMenu", action["extra"]["class"])
        set_selected_default_skin(self.folder, skins[0])
        self.assertEqual(skins[0], get_selected_default_skin(self.folder))
        actions = self.menu.getMenuItems(self.folder, self.request)
        action = [a for a in actions if a["title"] == skins[0]][0]
        self.assertEqual("actionMenuSelected", action["extra"]["class"])


class TestSelectSkinView(base.BaseFunctionalTestCase):

    def afterSetUp(self):
        self.basic_auth = "%s:%s" % (ptc.default_user, ptc.default_password)
        self.folder_path = self.folder.absolute_url(1)
        self.portal_path = self.portal.absolute_url(1)

    def testSwitchDefaultSkin(self):
        response = self.publish(
            self.folder_path + '/@@switchDefaultSkin?skin_name=Sunburst%20Theme',
            basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(self.folder.absolute_url(),
                         response.getHeader("Location"))
        self.assertTrue(hasattr(aq_base(self.folder), HOOK_NAME))
        self.assertTrue(isinstance(getattr(aq_base(self.folder), HOOK_NAME),
                                   LocalSiteHook))

        btr = queryBeforeTraverse(self.folder, HOOK_NAME)[0]
        self.assertEqual(1, btr[0])
        self.assertTrue(isinstance(btr[1], AccessRule))
        self.assertEqual(HOOK_NAME, btr[1].name)
        ns = IAnnotations(self.folder).get(ANNOTATION_KEY, None)
        self.assertNotEqual(None, ns)
        self.assertEqual("Sunburst Theme", ns["default-skin"])

    def testAnotherMemberCannotSelectSkin(self):
        membership_tool = getToolByName(self.folder, 'portal_membership')
        membership_tool.addMember("anotherMember", "secret", ['Member'], [])
        response = self.publish(
            self.folder_path + '/@@switchDefaultSkin?skin_name=Sunburst%20Theme',
            basic="anotherMember:secret")
        self.assertEqual(response.getStatus(), 302)
        self.assertFalse(self.folder.absolute_url() ==
                         response.getHeader("Location"))
        self.assertFalse(hasattr(aq_base(self.folder), HOOK_NAME))
        ns = IAnnotations(self.folder).get(ANNOTATION_KEY, None)
        self.assertEqual(None, ns)

    def testSkinSwitchedOnFakeTraversalEvent(self):
        response = self.publish(
            self.folder_path + '/@@switchDefaultSkin?skin_name=Sunburst%20Theme',
            basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(self.folder.absolute_url(),
                         response.getHeader("Location"))

        # Create new skin based on Sunburst Theme and make this the
        # default skin.
        new_default_skin(self.portal)
        self.assertEqual("Monty Python Skin", self.folder.getCurrentSkinName())

        request = TestRequest(SERVER_URL='http://localhost')
        event = FakeTraversalEvent(self.folder, request)
        switch_skin(self.folder, event)
        self.assertEqual("Sunburst Theme", self.folder.getCurrentSkinName())
        self.assertEqual(0, request.get("editskinswitched", 0))

    def testSkinSwitchedOnRealTraversalEvent(self):
        # Create new skin based on Sunburst Theme and make this the
        # default skin.
        new_default_skin(self.portal)
        response = self.publish(
            self.folder_path + '/getCurrentSkinName',
            basic=self.basic_auth)
        self.assertEqual("Monty Python Skin", response.getBody())

        response = self.publish(
            self.folder_path + '/@@switchDefaultSkin?skin_name=Sunburst%20Theme',
            basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(self.folder.absolute_url(),
                         response.getHeader("Location"))

        response = self.publish(
            self.folder_path + '/getCurrentSkinName',
            basic=self.basic_auth)
        self.assertEqual("Sunburst Theme", response.getBody())


class TestSelectSkinFallbackForm(base.BaseFunctionalTestCase):
    # The fallback form is the form that is shown when you click on
    # the menu and you do not have javascript enabled

    def _login(self, browser, login_name=ptc.default_user):
        portal_url = self.portal.absolute_url()
        browser.open(portal_url + '/logout')
        browser.open(portal_url + '/login_form')
        browser.getControl(name='__ac_name').value = login_name
        browser.getControl(name='__ac_password').value = ptc.default_password
        browser.getControl(name='submit').click()

    def testSkinSwitchUsingFallbackForm(self):
        self.loginAsPortalOwner()
        folder_url = self.folder.absolute_url()
        portal_url = self.portal.absolute_url()
        # Add a second folder:
        self.portal.invokeFactory('Folder', id='folder2')
        folder2 = self.portal.folder2
        wf_tool = getToolByName(self.portal, 'portal_workflow')
        wf_tool.doActionFor(folder2, 'publish')
        folder2_url = folder2.absolute_url()
        # Add a sub folder:
        folder2.invokeFactory('Folder', id='sub_folder')
        sub_folder = folder2.sub_folder
        wf_tool.doActionFor(sub_folder, 'publish')
        sub_folder_url = sub_folder.absolute_url()
        # Create a new default skin.
        new_default_skin(self.portal)

        # Set the default skin for the first folder.
        browser = Browser()
        browser.handleErrors = False
        self._login(browser)
        browser.open(folder_url + "/select_skin")
        control = browser.getControl(name="skin_name")
        self.assertEqual([], control.value)
        control.value = ["Monty Python Skin"]

        # Saving the form redirects back to the folder.
        browser.getControl(name="form.button.Save").click()
        self.assertEqual(folder_url, browser.url)

        # Going back to the form has the skin selected.
        browser.open(folder_url + "/select_skin")
        control = browser.getControl(name="skin_name")
        self.assertEqual(["Monty Python Skin"], control.value)

        # Set the default skin for the second folder.  We have to do
        # this as portal owner.
        self._login(browser, login_name=ptc.portal_owner)
        browser.open(folder2_url + "/select_skin")
        control = browser.getControl(name="skin_name")
        self.assertEqual([], control.value)
        control.value = ["Sunburst Theme"]
        browser.getControl(name="form.button.Save").click()
        browser.open(folder2_url + "/select_skin")
        control = browser.getControl(name="skin_name")
        self.assertEqual(["Sunburst Theme"], control.value)

        # Set a different default skin for the sub folder.
        browser.open(sub_folder_url + "/select_skin")
        control = browser.getControl(name="skin_name")
        self.assertEqual([], control.value)
        control.value = ["Monty Python Skin"]
        browser.getControl(name="form.button.Save").click()
        browser.open(sub_folder_url + "/select_skin")
        control = browser.getControl(name="skin_name")
        self.assertEqual(["Monty Python Skin"], control.value)

        # What is the current skin name in a few contexts?
        self._login(browser)
        browser.open(portal_url + '/getCurrentSkinName')
        self.assertEqual(browser.contents, 'Monty Python Skin')
        browser.open(folder_url + '/getCurrentSkinName')
        self.assertEqual(browser.contents, 'Monty Python Skin')
        browser.open(folder2_url + '/getCurrentSkinName')
        self.assertEqual(browser.contents, 'Sunburst Theme')
        browser.open(sub_folder_url + '/getCurrentSkinName')
        self.assertEqual(browser.contents, 'Monty Python Skin')

        # Check the effect this has when visiting these contexts.  We
        # do this with an almost empty browser view that shows a
        # viewlet that is specifically registered for the Monty Python
        # theme and not the Sunburst Theme theme.  Plus a viewlet that
        # shows which marker interfaces the request provides.

        # First the portal root:
        browser.open(portal_url + '/@@viewlet-test')
        self.assertTrue('We want a shrubbery!' in browser.contents)
        self.assertTrue('interfaces.IMyTheme' in browser.contents)

        # Then the first folder:
        browser.open(folder_url + '/@@viewlet-test')
        self.assertTrue('We want a shrubbery!' in browser.contents)
        self.assertTrue('interfaces.IMyTheme' in browser.contents)

        # Then the second folder:
        browser.open(folder2_url + '/@@viewlet-test')
        self.assertFalse('We want a shrubbery!' in browser.contents)
        self.assertFalse('interfaces.IMyTheme' in browser.contents)

        # Then the sub folder:
        browser.open(sub_folder_url + '/@@viewlet-test')
        self.assertTrue('We want a shrubbery!' in browser.contents)
        self.assertTrue('interfaces.IMyTheme' in browser.contents)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentMenu))
    suite.addTest(makeSuite(TestSkinsMenu))
    suite.addTest(makeSuite(TestSelectSkinView))
    suite.addTest(makeSuite(TestSelectSkinFallbackForm))
    return suite
