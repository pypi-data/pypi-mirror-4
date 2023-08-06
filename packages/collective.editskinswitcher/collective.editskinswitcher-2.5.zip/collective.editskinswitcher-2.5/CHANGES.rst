Changelog for collective.editskinswitcher
=========================================

2.5 (2013-02-15)
----------------

- Nothing changed yet.


2.4 (2012-09-13)
----------------

- Added dependencies for Plone 4.2 compatibility:
  zope.app.publication and zope.app.publisher.
  [maurits]

- Moved to github:
  https://github.com/collective/collective.editskinswitcher
  [maurits]


2.3 (2012-04-11)
----------------

- using Sunburst Theme as default theme (we are now in Plone 4 country 
  since a while)
  [ajung]


2.2 (2012-02-15)
----------------

- Fixed broken release by fixing MANIFEST.in.
  [maurits]


2.1 (2012-02-15)
----------------

- Changed the calculation for the iframe height.  With the original
  code Firefox was behaving quircky, the height was 150px.  That is
  too small.  With help of Mark we could fix this.
  [mirella]


2.0 (2011-09-28)
----------------

- Added MANIFEST.in so we can automatically include .mo files with
  zest.pocompile.
  [maurits]

- Replace the PAGE_WHITE_LIST and SUFFIX_WHITE_LIST with a list of
  regular expressions (WHITELIST_REGEXPS). Using regexps we can also
  whitelist more complex URLs, e.g. for the password reset tool
  (/passwordreset/1234...). [markvl]


1.6 (2011-06-11)
----------------

- Also set the theme specific browser layers when switching skins.
  Code heavily inspired by themetweaker.themeswitcher. [markvl]


1.5 (2011-01-04)
----------------

- Always show the Styles menu when the user has the "Set navigation
  root" permission.
  [maurits]

- Check our permissions on the folder when we are on a default page.
  This might give a difference.
  [maurits]


1.4 (2010-12-31)
----------------

- Added menu item to set the context as a navigation root
  (plone.app.layout.navigation.interfaces.INavigationRoot) guarded by
  new permission "Set navigation root", by default only for Manager.
  [maurits]


1.3 (2010-12-14)
----------------

- Do not show the Styles menu when there are no styles to choose.
  [maurits]

- Moved PAGE_WHITE_LIST and SUFFIX_WHITE_LIST from traversal.py to new
  config.py.
  [maurits]

- Added SUFFIX_WHITE_LIST to avoid triggering a forced login for css
  or javascript files, otherwise the login form will look ugly.  Also
  added logo.jpg/png/gif and favicon.ico to the PAGE_WHITE_LIST for
  the same reason.
  [maurits]


1.2 (2010-12-07)
----------------

- Do not force logging in when you get this header for a login page
  (specified by the PAGE_WHITE_LIST).
  [maurits]


1.1 (2010-12-07)
----------------

- Use ``get_header`` instead of ``get`` when looking for headers to
  force logging in or force using the edit skin.
  [maurits]

- Allow setting a default skin on a folder, using the new Styles
  context menu.
  [dreamcatcher]


1.0 (2010-06-07)
----------------

- Fix: when we need authentication and we are anonymous then we do
  *not* want to switch: we want to have the default behaviour of
  getting the standard skin instead of the edit skin.  Added some more
  inline documentation.
  [maurits]

- Switch back to checking the ``__ac`` cookie to see if someone is
  anonymous or not; the getSecurityManager check always says we are
  anonymous, though I thought I had seen it working previously.
  [maurits]

- Add logging lines for debugging.
  [maurits]


0.9 (2010-04-19)
----------------

- Change the switch skin action to a multiple selection.  When one
  of the selected actions returns True, we switch the skin.
  [maurits]

- Also accept urls like admin.example.org as edit urls.
  [maurits]


0.8 (2010-04-16)
----------------

- Slightly better check for anonymous users, using getSecurityManager
  instead of checking for an ``__ac`` cookie.
  [maurits]

- When a X_FORCE_LOGIN header is passed (exact spelling is configurable)
  only allow access to logged in users (you get redirected usually).
  [maurits]

- Allow specifying the admin_header; defaults to HTTP_PLONEADMIN.
  [maurits]

- Added z3c.autoinclude.plugin entry point for plone, to avoid having
  collective.editskinswitcher in the zcml option of your zope
  instance; only effective in Plone 3.3 or higher.  In earlier
  versions you still need to do this manually.
  [maurits]


0.7 (2008-10-04)
----------------

- Added switching option based on a request header flag set by the
  proxy server (eg. Apache)
  [Ed Crewe, ILRT - University of Bristol]


0.6 (2008-08-27)
----------------

- New preview feature so that the default skin can be seen via the
  edit skin interface to preserve some level of WYSIWYG for editing.
  (Based on part of an unreleased plone 2 product by Dominic Hiles.)
  Preview feature is available as a viewlet for use via a view or a
  viewletManager, but it is turned off by default.  Examples of how to
  enable it are included in the tests, where it is enabled and tested.
  [Ed Crewe, ILRT - University of Bristol]

- Extra URL skin switching options of SSL or specific URLs
  [Ed Crewe, ILRT - University of Bristol]

- Setting eol style in subversion correctly. [reinout]


0.5 (2008-03-07)
----------------

- Bug fix: when called on the zope root (can happen in some cases)
  portal_properties was not found, which was not caught correctly.
  [maurits]


0.4 (2008-02-12)
----------------

- Bug fix: if object has no changeSkin, try its context.  Happens at
  least on the sharing tab when searching for users, as object is a
  KSS view then.
  [maurits]


0.3 (2008-01-30)
----------------

- Instead of an Access Rule, use a pre-traversal hook.  Idea: David
  Convent.  Thanks!  Is a lot cleaner.
  [maurits]

- Avoid confusion in README.txt: talk about Editor Skin and Visitor
  Skin instead of Plone Default and the default skin.
  [maurits]

- Update README.txt to tell about the new options introduced in
  version 0.2.
  [maurits]


0.2 (2008-01-28)
----------------

- When testing if the user is logged in, check for the __ac cookie in
  the request instead of portal_membership.isAnonymousUser as this
  does not work in real life; probably because we use an AccessRule.
  [maurits]

- Add based_on_url property (default: True).  When True, the skin
  switching is done when you visit the site via an edit url.  When
  combined with need_authentication=True, only logged-in users on the
  edit url get the edit skin.
  [maurits]

- Add need_authentication property (default: False).  When True, the
  skin switching is only done when you are authenticated (logged in).
  [maurits]

- In the base test cases, create the new default skin.
  [maurits]

- Split tests/setup.txt in two files for separating some unrelated
  tests.
  [maurits]

- Add a more readable README.txt and move the old one into the
  tests directory as it contains most of our tests.
  [maurits]


0.1 (2008-01-25)
----------------

- Add a property sheet editskin_switcher with property edit_skin.
  Default value: Plone Default.  Use that for determining which
  skin to give to editors.
  [maurits]

- Initial package structure.
  [zopeskel]
