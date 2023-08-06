import logging

from AccessControl import Unauthorized, getSecurityManager
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.interface import noLongerProvides, alsoProvides
from zope.publisher.interfaces.browser import IBrowserSkinType

from collective.editskinswitcher.skin import get_selected_default_skin
from collective.editskinswitcher.config import WHITELIST_REGEXPS

logger = logging.getLogger('editskinswitcher')


def anonymous(request=None):
    if request is None:
        # I thought I had seen this working, but under normal
        # circumstances when traversing you are always anonymous...
        logger.debug("No request passed in")
        anon = (getSecurityManager().getUser().getUserName() ==
                'Anonymous User')
    elif request.cookies.get('__ac'):
        anon = False
    else:
        anon = True
    logger.debug("Anonymous? %s", anon)
    return anon


def check_auth(request):
    if anonymous(request):
        raise Unauthorized('Go away')


def edit_url(request, props):
    ''' The default switch check based on a subdomain of cms, edit or manage'''
    from collective.editskinswitcher.utils import is_edit_url
    val = is_edit_url(request.getURL())
    logger.debug("Is edit url? %s", val)
    return val


def specific_domain(request, props):
    specific_domains = props.getProperty('specific_domains', ())
    if specific_domains != ():
        thisurl = request.getURL()
        if thisurl in specific_domains:
            logger.debug("This url is in a specific domain.")
            return True
    logger.debug("This url is NOT in a specific domain.")
    return False


def ssl_url(request, props):
    parts = request.getURL().split('://')
    if parts[0] == 'https':
        logger.debug("https url")
        return True
    logger.debug("normal http url")
    return False


def force_login(request, props):
    force_login_header = props.getProperty('force_login_header', None)
    if not force_login_header:
        return False

    # Note: to truly test what happens when forcing login via a header
    # on your local machine without any Apache setup, you should
    # comment out this condition:
    if not request.get_header(force_login_header, None):
        logger.debug("Login will NOT be forced.")
        return False

    # Okay, login should be forced, except when this url is in a white
    # list.
    actual_url = request.get('ACTUAL_URL', '')
    logger.debug("ACTUAL_URL: %s", actual_url)
    for regexp in WHITELIST_REGEXPS:
        if regexp.search(actual_url):
            logger.debug('NOT forcing login: %s is in white list' %
                         regexp.pattern)
            return False
    logger.debug("Login will be forced.")
    return True


def admin_header(request, props):
    admin_header = props.getProperty('admin_header', 'HTTP_PLONEADMIN')
    if request.get_header(admin_header, None):
        logger.debug("admin header found")
        return True
    logger.debug("no admin header found")
    return False


def need_authentication(request, props):
    """This is for skin switching based on authentication only."""
    val = props.getProperty('need_authentication', False)
    logger.debug("Need authentication? %s", val)
    return val


methods = {'based on edit URL': edit_url,
           'based on specific domains': specific_domain,
           'based on SSL': ssl_url,
           'based on admin header': admin_header,
           'no URL based switching': need_authentication}


def get_real_context(object):
    # object might be a view, for instance a KSS view.  Use the
    # context of that object then.
    try:
        getattr(object, 'changeSkin')
    except AttributeError:
        return object.context
    return object


def set_theme_specific_layers(request, context, new_skin, current_skin):
    # remove theme specific layer of the current skin
    current_skin_iface = queryUtility(IBrowserSkinType, name=current_skin)
    if current_skin_iface is not None:
        noLongerProvides(request, current_skin_iface)
    # check to see the skin has a BrowserSkinType and add it.
    skin_iface = queryUtility(IBrowserSkinType, new_skin)
    if skin_iface is not None and not skin_iface.providedBy(request):
        alsoProvides(request, skin_iface)


def switch_skin(object, event):
    """Switch to the Sunburst Theme skin when we are editing.

    Note: when we bail out before the changeSkin call, then we show
    the normal theme, which presumably is a custom theme for this
    website.

    If we do the changeSkin call, this means we switch to the edit
    skin, which normally is the Sunburst Theme skin.
    """
    request = event.request
    context = get_real_context(object)
    current_skin = context.getCurrentSkinName()
    skin_name = get_selected_default_skin(context)
    if skin_name is not None and not request.get('editskinswitched'):
        # We've specified a skin and are not in the edit skin.
        portal_skins = getToolByName(context, 'portal_skins', None)
        if (portal_skins is not None and
                skin_name not in portal_skins.getSkinSelections()):
            logger.warn("Non-existing skin %s set on %s",
                        skin_name, context.absolute_url())
        else:
            context.changeSkin(skin_name, request)
            set_theme_specific_layers(request, context, skin_name,
                                      current_skin)

    portal_props = getToolByName(context, 'portal_properties', None)
    if portal_props is None:
        return None
    editskin_props = portal_props.get('editskin_switcher')
    if editskin_props is None:
        return None

    # Okay, we have a property sheet we can use.
    edit_skin = editskin_props.getProperty('edit_skin', '')

    if force_login(request, editskin_props):
        # We have a header that forces us to be logged in; so add a
        # hook at the end of the traversal to check that we really are
        # logged in.
        request.post_traverse(check_auth, (request, ))

    # Check if we need authentication first, possibly in addition to
    # one of the other tests
    if need_authentication(request, editskin_props) and anonymous(request):
        logger.debug("need auth, but am anonymous: staying at normal skin.")
        return None

    # Try to find a reason for switching to the edit skin.  When one
    # of the selected actions returns True, we switch the skin.
    switches = editskin_props.getProperty('switch_skin_action', ())
    if not isinstance(switches, tuple):
        # Old data using a selection instead of multiple selection,
        # which returns a string instead of a tuple of strings.
        switches = (switches, )

    found = False
    for switch in switches:
        method = methods.get(switch)
        if not method:
            continue
        if method(request, editskin_props):
            found = True
            break
    if not found:
        # No switching
        logger.debug("no switching, staying at normal skin")
        return None

    logger.debug("will switch to edit skin")

    # Use to preview default skin in edit skin mode
    if request.get('mutate_skin', '') == 'default':
        return None

    # Assume that if you get here you are switching to the edit skin
    # ... flag this for the purposes of caching / kss loading etc.
    request.set('editskinswitched', 1)

    # If the edit_skin does not exist, the next call is
    # intelligent enough to use the default skin instead.
    context.changeSkin(edit_skin, request)
    set_theme_specific_layers(request, context, edit_skin, current_skin)
    return None
