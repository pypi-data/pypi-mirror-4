README for collective.editskinswitcher tests skins
==================================================

This skins directory is currently just used for tests. It contains two 
subfolders:

1. editskinswitcher_tests

This contains a dummy accessibility-info file. It is of no practical 
use in itself.
It is simply there to provide different identifiable content in the 
default skin from that present in the standard edit skin.

2. editskinswitcher_edit_content

The second folder contains a replacement for the default document_view 
template, used for viewing standard plone pages. It calls the replace 
content viewlet manager which in turn contains the preview viewlet iframe.
It is used to test that the option to replace view with preview works OK 
via browser tests.

It can be used as a template to replace all plone_content (or third 
party product content) templates in the edit skin. 

It simply replaces the standard archetype widget view slot ...

        <metal:field use-macro="python:here.widget('text', mode='view')">
        Body text
        </metal:field>

... with the following ...

        <div tal:replace="structure provider:editskinswitcher.replacecontent" />


Instructions on how to replace view with preview in a theme egg
===============================================================

To use the preview function to replace view in your edit skin, add this 
edit_content skin folder to your default theme egg and register for use 
with the edit layer for your implementation, eg. 'Sunburst Theme'

The following steps explain how this is done:

1. Copy the tests/skins/editskinswitcher_edit_content directory to a 
   skins/yourtheme_edit_content directory in your theme egg

2. Add the line below to your configure.zcml (or a skins.zcml included in it)

   <cmf:registerDirectory name="yourtheme_edit_content" directory="skins/yourtheme_edit_content" recursive="False" />

3. Add a layer for your edit skin to the same file

    <interface
        interface=".interfaces.IYourThemeAdminThemeSpecific"
        type="zope.publisher.interfaces.browser.IBrowserSkinType"
        name="yourtheme_editskin"
        />

4. Register that skin against your edit layer in the profile skins.xml 
   Below is an example profiles/default/skins.xml file that does this.

<?xml version="1.0"?>
<!-- This file holds the setup configuration for the portal_skins tool -->
<object name="portal_skins" allow_any="False" cookie_persistence="False" default_skin="yourtheme_defaultskin">

 <object name="yourtheme_edit_content"
    meta_type="Filesystem Directory View"
    directory="your.theme:skins/yourtheme_edit_content"/>

 <skin-path name="yourtheme_editskin" based-on="Sunburst Theme">
  <layer name="yourtheme_edit_content" insert-after="custom"/>
 </skin-path>

</object>

5. Restart zope and add a yourtheme plone site.


[Ed Crewe]
