import monkeypatches
monkeypatches  # pyflakes

from zope.i18nmessageid import MessageFactory
SwitcherMessageFactory = MessageFactory('editskinswitcher')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
