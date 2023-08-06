import re

# Used in the force_login function to avoid forcing a login for pages
# that are used in the login process.
# List mostly taken from
# Products/CMFPlone/skins/plone_login/login_next.cpy (some removed)
WHITELIST_REGEXPS_PATTERNS = [
    '/login_success$', '/login_password$', '/login_failed$',
    '/login_form$', '/logged_in$', '/logged_out$', '/registered$',
    '/mail_password$', '/mail_password_form$', '/join_form$',
    '/require_login$', '/member_search_results$', '/pwreset_finish$',
    '/passwordreset/[a-f0-9]*$', '/pwreset_form$',
    # Allow some pictures:
    '/favicon.ico$', '/logo.jpg$', '/logo.png$', '/logo.gif$',
    # We'll need some CSS and JavaScript
    '\.css$', '\.js$']

# We'll be using the regexps quite a lot, so we want them compiled.
WHITELIST_REGEXPS = [re.compile(r) for r in WHITELIST_REGEXPS_PATTERNS]

# When you set a default skin on a folder, we add a local site hook to
# register a beforeTraverse event.  When resetting the default skin we
# should normally remove the local site hook.  But this might not
# always be the best idea.  Others might be using the local site hook
# as well.  So here we make it configurable in case someone is badly
# affected:
REMOVE_LOCAL_SITE_HOOK = True
