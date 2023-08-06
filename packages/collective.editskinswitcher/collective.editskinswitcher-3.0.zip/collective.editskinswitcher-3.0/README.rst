.. contents::

Collective edit skin switcher
=============================

For a customer of `Zest Software`_ I [Maurits van Rees] created a
package called ``collective.editskinswitcher``.  I gladly took some code
from colleague Mark van Lent who did something similar for a different
web site.  The package is on the Cheese Shop so it can be easy
installed.  And the code is in the Plone github collective_.

.. _`Zest Software`: http://zestsoftware.nl
.. _collective: https://github.com/collective/collective.editskinswitcher


Compatibility
-------------

``collective.editskinswitcher`` 3.0 is compatible with Plone version
4.1 until and including 4.3.  For earlier Plone versions please use
``collective.editskinswitcher`` 2.x.


What does it do?
----------------

Let's say you have a Plone Site.  I tested this with Plone 3.  I see
no reason why it should fail on Plone 2.5.  Maybe it even works on a
CMF site.  Anyway, whatever site you have is available on two urls:
``www.example.com`` and ``edit.example.com``.  Some day you
should ask your local Apache guru how he did that.

With ``collective.editskinswitcher`` installed (with the portal quick
installer), visitors that go to the website with the url
``edit.example.com`` will see the Editor Skin.  (This can be set in
a property, as we shall see later.)  Visitors to
``www.example.com`` will see whatever skin you have set as the
default skin in portal_skins.  Can be pretty handy.

To avoid confusion: we will call what you have set as "default skin"
the Visitor Skin.  And the skin meant for editors we call the Editor
Skin.

Developer types probably like the fact that you also get the Visitor
Skin when visiting ``localhost`` and the Editor Skin when you go to
``127.0.0.1``.

You can also set a different default skin in a
folder.  So you can set it up so that folder-1 uses a red theme,
folder-2 a blue theme and when you edit either folder you still use
Sunburst Theme.  See also the `Per-folder default skin`_ section.


Other options
-------------

There are some options you can set.  Go to ``portal_properties``, and
then go to the ``editskin_switcher`` property sheet.  These options
are available:

- ``edit_skin``: set the skin that editors get.  The default is "Plone
  Default".

- ``switch_skin_action``: choose the url condition that is used for
  switching to the edit skin.  Note: this is a multiple select: if
  *one* of the selected options gives a positive result, then we
  switch to the edit skin.  Options are:

  - based on edit URL: With this you get the behaviour described above.
    This is the default.

  - based on specific domain: If this is specified the edit skin is
    used when the first part of the url matches one of the entries in
    the ``specific_domains`` property.  This url is the url for the
    root of the Plone Site; so usually this will be a domain, like
    ``http://special.example.com/``.  Note that you need to very
    explicitly use the exact url to your Plone Site root.  For
    example, when trying this locally you may need something like
    this: ``http://localhost:8080/Plone``

  - based on admin header: If this is chosen you will need to set up your proxy
    server, eg. Apache, to add a 'HTTP_PLONEADMIN' header to the request. It can
    do this based on the url for instance. An example is given in
    /tests/ploneadmin_header.txt

  - based on SSL: If this is chosen, then any urls that are SSL
    will get the edit skin and others will get the default skin.

  - No URL based switching: do not base the skin switching on the url;
    instead we check the ``need_authentication`` option.

- ``need_authentication``: when True you need to be logged in before
  your skin is switched.  By default this is set to False.  See
  the section `Am I authenticated?`_ below for some notes.

- ``force_login_header``: when the request has this header, only
  authenticated use is allowed.  This does not actually switch the
  skin; you just get redirected to the login_form.  By default this is
  set to the string ``X_FORCE_LOGIN``.  Note that this is not done for
  the login_form and other pages like that.  Such a page probably
  looks ugly though, as you still are forced to login before you can
  get the css and images for that page.

If you combine the switch skin action and the authentication, then you
need to have the right url and you need to be logged in.

When both are not used, nothing happens: then you might as well simply
uninstall this product as it is not useful.


Am I authenticated?
-------------------

The ``need_authentication`` option looks for the ``__ac`` cookie that
Plone gives you when logged in.  There are a few possible problems
with this:

- Logging in via the Zope Management Interface is handled without
  cookies, so the editskin switcher regards you as anonymous then.

- We do not check if the the cookie is actually valid.  This can
  mostly give a surprise when you are developing multiple websites on
  your own local computer: Plone stores the ``__ac`` cookie for the
  localhost domain, without differentiating between multiple Plone
  sites.  So if you are logged into Plone Site A on localhost with a
  cookie, then the skin switcher thinks you are authenticated for all
  websites on localhost.

Alternatively, we could check ``getSecurityManager().getUser()``, but
that check always thinks we are anonymous, presumably because our
check is done during traversal, which apparently is too soon for
anyone to be recognized as being logged in.


Why not CMFUrlSkinSwitcher?
---------------------------

I looked at CMFUrlSkinSwitcher first but it had not been touched in
two years.  One import error (CMFCorePermissions) could easily be
fixed as that import was not even used.  But after that tests were
failing all over the place.  Theoretically always fixable of course,
but rolling an own package seemed easier, cleaner and faster.

Also, CMFUrlSkinSwitcher does some more things.  At least it messes
around with some methods like absolute_url.  It could be that I find
out later that this is necessary in ``collective.editskinswitcher`` too,
but currently it does not look like that will be the case.


How do I know this is working?
------------------------------

The easiest way to test this package in a default plone site (apart
from running the tests of course), is:

- Install ``collective.editskinswitcher``.

- Go to portal_skins in the ZMI.

- Create a new skin selection based on Sunburst Theme.  Call this
  "Visitor Skin".

- Make Visitor Skin the default skin.

- Remove the custom skin layer from Sunburst Theme.

- Customize the main template or the logo or something else that
  is easy to spot.

- Visit ``127.0.0.1:8080/plonesite`` and you will see default Plone.

- Visit ``localhost:8080/plonesite`` and you will see Plone with
  your customization.


On Linux you can edit ``/etc/hosts`` and add a line like::

  127.0.0.1 edit.example.com www.example.com

Now visiting ``edit.example.com`` should give you the Editor Skin
and ``www.example.com`` should give you the Visitor Skin with the
customizations.


You can also let the edit urls begin with ``cms`` or ``manage``.  As
long as the url is something like::

  ...//(edit|cms|manage).something.something....

you end up in the edit skin.


Preview
-------

The preview option allows you to see the default skin via the edit skin.

It does so by using an iframe which accesses the edit skin content but flips
it to the default skin. This allows you to easily view previous versions,
private content etc. as it will appear in the default skin if published.

This is particularly useful in cases where your default skin differs
radically from the edit skin. It allows the edit interface to maintain some
wysiwyg functionality.

Preview can either be used as a separate preview tab, or as a replacement
for the view tab content in the edit skin.

Both are implemented within the tests folder and tested, but neither is
used by default.

For the preview of editskinswitcher to be of use it requires an
accompanying theme.egg holding the configuration for the default (and
edit) skins.  In order to use preview, it must be turned on within
this accompanying theme egg. Example code to do this are within the
tests folder.

Instructions for replacing view with preview are given in
tests/skins/README.txt

To add it as a separate preview tab:

1. Add the browser view by putting what is in testing.zcml in your
   theme egg configure.zcml or loading that file in the part of your
   buildout that creates the ``zope2instance``, something like::

     zcml =
         collective.editskinswitcher-testing

2. Within tests/add_preview.py there is ACTIONSCONFIG
   Add this as a profiles/default/actions.xml file.
   Change the default visible=False property to True.  Or do it by
   hand by going to portal_actions, object, and adding a preview
   action with url expression ``string:${object_url}/@@preview``.

Note that it looks like currently our ``++resourece++iframe.js`` is
not properly loaded, which in my tests unhelpfully makes the iframe
about two centimeters high, though that probably depends on what you
have set as the edit skin.  If you use this feature and are hit by
this bug and maybe even know how to fix it, contact me.


Per-folder default skin
-----------------------

Selecting a default skin for a specific folder is also supported. A
'Skins' menu entry should show up in the content area, right next to
the 'Display' and 'Actions' menu. Once you select a skin from that
dropdown, it will be used as the default skin when visiting that
folder instead of the site-wide default skin.

This menu is available for everyone who has the ``Set default skin``
permission, which by default is for Managers and Owners.  So if you do
not want anyone to have this menu, you can do so by not giving anyone
this permission.  In the rolemap.xml file of your GenericSetup profile
that would look like this::

  <?xml version="1.0"?>
  <rolemap>
    <permissions>
     <permission name="Set default skin" acquire="False" />
    </permissions>
  </rolemap>


Sub sites with navigation root
------------------------------

Using the `Per-folder default skin`_ menu you already mostly have a to
make simple subsites.  The only other basic thing needed is to set the
folder as a navigation root, so giving it the
``plone.app.layout.navigation.interfaces.INavigationRoot`` marker
inferface.  This option has now been added to the menu, guarded by new
permission "Set navigation root", by default only for Manager.


Installation using zc.buildout
------------------------------

For using collective.editskinswitcher with zc.buildout you have to add
``collective.editskinswitcher`` to the ``eggs`` section::

   eggs = collective.editskinswitcher
   ...


Have fun!

Maurits van Rees
