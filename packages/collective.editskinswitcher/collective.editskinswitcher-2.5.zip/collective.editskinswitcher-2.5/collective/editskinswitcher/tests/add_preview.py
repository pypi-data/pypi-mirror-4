### Handler that modifies skins and actions tools - just used for
### tests.  If you want to use preview then either add it as an action
### tab using the actions.xml below or add the
### test/skins/editskinswitcher_edit_content to your edit skin to
### replace the standard edit view

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.exportimport.actions import importActionProviders
from Products.GenericSetup.tests.common import DummyImportContext

ACTIONSCONFIG = """\
<?xml version="1.0"?>
<object name="portal_actions" meta_type="Plone Actions Tool"
    xmlns:i18n="http://xml.zope.org/namespaces/i18n">

 <object name="object" meta_type="CMF Action Category">
  <property name="title"></property>

  <object name="skinpreview" meta_type="CMF Action" i18n:domain="plone">
    <property name="title" i18n:translate="">Preview</property>
    <property name="description" i18n:translate=""></property>
    <property name="url_expr">string:${object_url}/@@preview</property>
    <property name="icon_expr"></property>
    <property name="available_expr"></property>
    <property name="permissions">
     <element value="View"/>
    </property>
    <property name="visible">False</property>
  </object>

 </object>
</object>
"""


def previewChange(context, props):
    """This toggles the preview tab and making view like preview."""
    preview = props.get('add_preview_tab', False)
    a_tool = getToolByName(context, 'portal_actions')
    ptabs = getattr(a_tool, 'object', None)
    if ptabs:
        prevtab = getattr(ptabs, 'skinpreview', None)
        if not prevtab:
            # Add the tab that points to the @@preview view
            importcontext = DummyImportContext(context, False)
            importcontext._files['actions.xml'] = ACTIONSCONFIG
            importActionProviders(importcontext)
            prevtab = getattr(ptabs, 'skinpreview')
        prevtab.visible = preview
    else:
        raise 'Sorry no portal actions tool - object actions found'

    changeview = props.get('change_view_into_preview', False)
    sk_tool = getToolByName(context, 'portal_skins')
    defaultpath = sk_tool.getSkinPath('Sunburst Theme')
    changed = defaultpath.find('editskinswitcher_edit_content') > -1
    if changeview != changed:
        sk_tool.manage_skinLayers(chosen=['Sunburst Theme'], del_skin=1)
        if changeview and not changed:
            if not getattr(sk_tool, 'editskinswitcher_edit_content', None):
                cmfcore = sk_tool.manage_addProduct['CMFCore']
                addDir = cmfcore.manage_addDirectoryView
                addDir(reg_key='collective.editskinswitcher:'
                       'tests/skins/editskinswitcher_edit_content',
                       id='editskinswitcher_edit_content')
            skinpath = 'editskinswitcher_edit_content,' + defaultpath
        elif not changeview and changed:
            skinpath = defaultpath.replace(
                'editskinswitcher_edit_content,', '')
        sk_tool.addSkinSelection('Sunburst Theme', skinpath)
