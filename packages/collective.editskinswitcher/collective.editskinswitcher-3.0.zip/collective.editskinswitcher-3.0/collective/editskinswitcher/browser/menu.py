from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from plone.memoize.instance import memoize
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.browsermenu.menu import BrowserMenu
from zope.browsermenu.menu import BrowserSubMenuItem
from plone.app.layout.navigation.interfaces import INavigationRoot

from collective.editskinswitcher import SwitcherMessageFactory as _
from collective.editskinswitcher.browser.interfaces import (
    ISkinsSubMenuItem, ISkinsMenu)
from collective.editskinswitcher.permissions import SetDefaultSkin
from collective.editskinswitcher.permissions import SetNavigationRoot
from collective.editskinswitcher.skin import get_selected_default_skin


class SkinsSubMenuItem(BrowserSubMenuItem):

    implements(ISkinsSubMenuItem)
    submenuId = "collective-editskinswitcher-menu-skins"
    title = _(u"Skins")
    description = _(u"Change skin for the current content item")
    extra = {'id': 'collective-editskinswitcher-menu-skins'}

    order = 11

    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.tools = getMultiAdapter((context, request), name='plone_tools')
        self.context_state = getMultiAdapter((context, request),
                                             name='plone_context_state')

    @property
    def folder(self):
        if self.context_state.is_structural_folder():
            return self.context
        return utils.parent(self.context)

    @property
    def action(self):
        return self.folder.absolute_url() + '/select_skin'

    @memoize
    def available(self):
        if self.context_state.is_portal_root():
            # Just use the portal_skins tool, Luke!
            return False

        # This menu is also used to set the navigation root, when
        # allowed.
        if self._allowSetNavigationRoot():
            return True

        if not self._manageSkinSettings():
            return False

        # Only allow this menu on folders.
        if not (self.context_state.is_structural_folder()
                or self.context_state.is_default_page()):
            return False

        # Check if our property sheet is available.  When not, then
        # this might be a second Plone site in the same Zope instance.
        # If we are not installed in this Plone Site, we do not want
        # to offer this menu item.
        if not self.tools.properties().get('editskin_switcher'):
            return False

        if get_selected_default_skin(self.folder):
            # We have previously selected a default skin, so we should
            # show the menu to make this clear (and possibly unset
            # it).
            return True

        skins_tool = getToolByName(self.context, 'portal_skins')
        if len(skins_tool.getSkinSelections()) < 2:
            # Nothing to choose.
            return False
        return True

    @memoize
    def _manageSkinSettings(self):
        return self.tools.membership().checkPermission(
            SetDefaultSkin, self.folder)

    @memoize
    def _allowSetNavigationRoot(self):
        return self.tools.membership().checkPermission(
            SetNavigationRoot, self.folder)

    def selected(self):
        return False


class SkinsMenu(BrowserMenu):
    implements(ISkinsMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []

        context_state = getMultiAdapter((context, request),
                                        name='plone_context_state')
        folder = context
        if not context_state.is_structural_folder():
            folder = utils.parent(context)
        url = folder.absolute_url()
        current_skin = get_selected_default_skin(folder)

        skins_tool = getToolByName(context, "portal_skins")
        skin_selections = skins_tool.getSkinSelections()

        # Only add menu items for skins when we have a choice or when
        # we have previously selected a default skin.  It could be
        # that this default skin has been removed and then we need a
        # way to unset it.
        tools = getMultiAdapter((context, request), name='plone_tools')
        if tools.membership().checkPermission(SetDefaultSkin, folder) and (
                len(skin_selections) > 1 or current_skin):
            if current_skin and current_skin not in skin_selections:
                # Skin has been removed.
                skin = current_skin
                skin_title = utils.safe_unicode(skin)
                skin_id = utils.normalizeString(skin, folder, "utf-8")
                results.append(
                    {"title": _(u"Warning: ${skin}",
                                mapping={'skin': skin_title}),
                     "description": _(
                         u"Skin '${skin}' no longer exists. Selecting this "
                         u"again will result in using the site default.",
                         mapping=dict(skin=skin_title)),
                     "action": "%s/@@switchDefaultSkin?skin_name=%s" % (
                         url, skin),
                     "selected": True,
                     "extra": {
                         "is_skin_option": True,
                         "id": "collective.editskinswitcher-skin-%s" % skin_id,
                         "separator": False,
                         "class": 'actionMenuSelected'},
                     "submenu": None,
                     "icon": None,
                     })

            for skin in skin_selections:
                skin_id = utils.normalizeString(skin, folder, "utf-8")
                skin_title = utils.safe_unicode(skin)
                selected = skin == current_skin
                cssClass = selected and "actionMenuSelected" or "actionMenu"
                results.append(
                    {"title": skin,
                     "description": _(u"Use '${skin}' skin for this folder",
                                      mapping=dict(skin=skin_title)),
                     "action": "%s/@@switchDefaultSkin?skin_name=%s" % (
                         url, skin),
                     "selected": selected,
                     "extra": {
                         "is_skin_option": True,
                         "id": "collective.editskinswitcher-skin-%s" % skin_id,
                         "separator": False,
                         "class": cssClass},
                     "submenu": None,
                     "icon": None,
                     })

        # Add option to reset the default.
        if current_skin:
            # Use a fake id that is unlikely to be the id of an actual skin.
            skin_id = 'collective_set_default_editor_use_site_default'
            results.append(
                {"title": _(u"Use site default"),
                 "description": u"",
                 "action": "%s/@@switchDefaultSkin?skin_name=%s" % (
                     url, skin_id),
                 "selected": False,
                 "extra": {
                     "is_skin_option": True,
                     "id": "collective.editskinswitcher-skin-%s" % skin_id,
                     "separator": 'actionSeparator',
                     "class": 'actionMenu'},
                 "submenu": None,
                 "icon": None,
                 })

        if tools.membership().checkPermission(SetNavigationRoot, folder):
            # Now add an option to set/unset the navigation root.
            menu_item = {
                "title": _(u"Navigation root"),
                "extra": {
                    "is_skin_option": False,
                    "id": "collective.editskinswitcher-set-navigation-root",
                    "separator": 'actionSeparator',
                    },
                "submenu": None,
                "icon": None,
                }
            if INavigationRoot.providedBy(folder):
                menu_item["selected"] = True
                menu_item["cssClass"] = "actionMenuSelected"
                menu_item["description"] = _(
                    u"No longer use this folder as a navigation root.")
                menu_item["action"] = "%s/@@unset-navigation-root" % (url)
            else:
                menu_item["selected"] = False
                menu_item["cssClass"] = "actionMenu"
                menu_item["description"] = _(
                    u"Start using this folder as a navigation root.")
                menu_item["action"] = "%s/@@set-navigation-root" % (url)
            results.append(menu_item)

        return results
