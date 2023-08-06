import logging
from Acquisition import aq_base
from Acquisition import aq_inner
from persistent.mapping import PersistentMapping
from zope.annotation.interfaces import IAnnotations
from Products.Five.component import LocalSiteHook, HOOK_NAME
from Products.SiteAccess.AccessRule import AccessRule
from ZPublisher.BeforeTraverse import registerBeforeTraverse
from ZPublisher.BeforeTraverse import unregisterBeforeTraverse

from collective.editskinswitcher import config

logger = logging.getLogger('collective.editskinswitcher')
ANNOTATION_KEY = "collective.editskinswitcher"


def get_selected_default_skin(context):
    """Get the selected default skin using annotations."""
    try:
        annotations = IAnnotations(context)
    except TypeError:
        # Not a context that we can handle (seen with
        # Products.CMFUid.UniqueIdAnnotationTool.UniqueIdAnnotation
        # when saving an object).
        return None
    ns = annotations.get(ANNOTATION_KEY, None)
    if ns is not None:
        return ns.get("default-skin", None)


def set_selected_default_skin(context, skin_name=None):
    """Set the specified skin name as the default skin using annotations.

    When the skin_name is None we can remove the annotation if it is there.
    """
    annotations = IAnnotations(aq_inner(context))
    ns = annotations.get(ANNOTATION_KEY, None)
    if ns is None and skin_name is not None:
        # First time here.  Create the annotation.
        ns = annotations[ANNOTATION_KEY] = PersistentMapping()
    elif ns is not None and skin_name is None:
        logger.info("Removed annotation.")
        del annotations[ANNOTATION_KEY]

    if skin_name is not None:
        logger.info("Set the default skin of %s to %s.",
                    context.absolute_url(), skin_name)
        ns["default-skin"] = skin_name


def add_hook(context):
    """Add local site hook with before traverse event.

    Check to see if the current object already has a LocalSiteHook
    from Five registered. If not, then register one ourselves, going
    around ``enableSite`` since we don't want to make this object a
    full ``ISite``, but just get the ``BeforeTraverseEvent`` fired.
    """
    base_object = aq_base(context)
    if hasattr(base_object, HOOK_NAME):
        return
    logger.info("Adding local site hook with before traverse hook at %s",
                context.absolute_url())
    hook = AccessRule(HOOK_NAME)
    registerBeforeTraverse(base_object, hook, HOOK_NAME, 1)
    setattr(base_object, HOOK_NAME, LocalSiteHook())


def remove_hook(context):
    """Remove local site hook with before traverse event.
    """
    base_object = aq_base(context)
    if not hasattr(base_object, HOOK_NAME):
        return
    logger.info("Unregistering before traverse hook at %s",
                context.absolute_url())
    unregisterBeforeTraverse(base_object, HOOK_NAME)
    # Now we should be able to remove the local site hook.  But this
    # might not always be the best idea.  Others might be using the
    # local site hook as well.  Let's at least make it configurable:
    if config.REMOVE_LOCAL_SITE_HOOK:
        logger.info("Removing local site hook at %s", context.absolute_url())
        delattr(base_object, HOOK_NAME)
    else:
        logger.info("Keeping local site hook at %s", context.absolute_url())
