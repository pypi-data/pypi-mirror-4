import logging
from zope.interface import alsoProvides, noLongerProvides
from Acquisition import aq_inner
from Products.CMFPlone.utils import getToolByName
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.component import getUtility
from zope.publisher.browser import BrowserView

try:
    # Try import that works in Zope 2.13 or higher first
    from zope.browsermenu.interfaces import IBrowserMenu
    IBrowserMenu  # pyflakes
except ImportError:
    # BBB for Zope 2.12 or lower
    from zope.app.publisher.interfaces.browser import IBrowserMenu

from collective.editskinswitcher import SwitcherMessageFactory as _
from collective.editskinswitcher.skin import (
    get_selected_default_skin, set_selected_default_skin,
    add_hook, remove_hook)

logger = logging.getLogger('collective.editskinswitcher')


class SelectSkin(BrowserView):

    def update(self):
        """Set selected skin as the default for the current folder."""
        context = aq_inner(self.context)
        utils = getToolByName(context, "plone_utils")

        # Which skin is requested?
        skin_name = self.request.form.get("skin_name", None)
        if skin_name is not None:
            skins_tool = getToolByName(context, 'portal_skins')
            if skin_name not in skins_tool.getSkinSelections():
                skin_name = None

        # Which skin is currently used as default skin, if any?
        current_skin = get_selected_default_skin(context)

        # Determine what needs to be done, and create or remove a
        # local site hook when needed.
        if skin_name is None and current_skin is None:
            utils.addPortalMessage(_(u"Nothing changed."))
        elif skin_name == current_skin:
            utils.addPortalMessage(_(u"Nothing changed."))
        elif skin_name is None and current_skin is not None:
            # Need to remove the hook.
            utils.addPortalMessage(_(u"No default skin selected anymore."))
            remove_hook(context)
        else:
            # The normal case: a change to the default skin.
            utils.addPortalMessage(_(u"Skin changed."))
            add_hook(context)

        # Finally set the default skin.  Note that this is safe to
        # call when skin_name is None as well, as this cleans up a
        # possible earlier setting.
        set_selected_default_skin(context, skin_name)

        return self.request.RESPONSE.redirect(context.absolute_url())

    def menuItems(self):
        """Return the menu items for the skin switcher."""
        menu = getUtility(
            IBrowserMenu, name="collective-editskinswitcher-menu-skins",
            context=self.context)
        return menu.getMenuItems(self.context, self.request)


class NavigationRoot(BrowserView):

    def set_navigation_root(self):
        context = aq_inner(self.context)
        if not INavigationRoot.providedBy(context):
            alsoProvides(context, INavigationRoot)
            logger.info("Activated navigation root at %s",
                        context.absolute_url())
            utils = getToolByName(context, "plone_utils")
            utils.addPortalMessage(_(u"Activated navigation root."))
        return self.request.RESPONSE.redirect(context.absolute_url())

    def unset_navigation_root(self):
        context = aq_inner(self.context)
        if INavigationRoot.providedBy(context):
            noLongerProvides(context, INavigationRoot)
            logger.info("Deactivated navigation root at %s",
                        context.absolute_url())
            utils = getToolByName(context, "plone_utils")
            utils.addPortalMessage(_(u"Deactivated navigation root."))
        return self.request.RESPONSE.redirect(context.absolute_url())
