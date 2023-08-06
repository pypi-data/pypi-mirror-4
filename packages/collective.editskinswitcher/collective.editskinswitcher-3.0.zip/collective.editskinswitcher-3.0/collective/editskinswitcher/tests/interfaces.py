# A browser layer - you should make one of these for your own skin
# and register it with a name corresponding to a skin in portal_skins.
# See tests.zcml and README.txt in plone.theme for more.

from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager


class IMyTheme(Interface):
    """Marker interface used in the tests
    """


class IMontyManager(IViewletManager):
    """Monty Python's Flying Viewlet Manager.
    """
