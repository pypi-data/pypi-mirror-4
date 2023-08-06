from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager
from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.interfaces import IBrowserSubMenuItem


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.

    If you need to register a view only for the editskinswitcher, this
    interface must be its layer
    """


class IPreviewView(Interface):
    """A separate preview page for an object

    It displays it as it appears in one skin for viewing within a
    different (edit) skin.
    """


class IPreviewViewlet(Interface):
    """A preview viewlet for replacing the default view content body

    It displays an object as it appears in one skin for viewing within
    a different (edit) skin.
    """


class IContentBodyViewletManager(IViewletManager):
    """A viewlet manager that replaces the normal content body of the page.
    """


class ISkinsSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the skins menu.
    """


class ISkinsMenu(IBrowserMenu):
    """The skins menu.

    This gets its menu items from registered skins.
    """
