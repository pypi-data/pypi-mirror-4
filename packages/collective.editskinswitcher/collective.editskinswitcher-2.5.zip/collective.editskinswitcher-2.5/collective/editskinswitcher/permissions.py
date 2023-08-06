from Products.CMFCore.permissions import setDefaultRoles

SetDefaultSkin = "Set default skin"
setDefaultRoles(SetDefaultSkin, ('Manager', 'Owner'))

SetNavigationRoot = "Set navigation root"
setDefaultRoles(SetNavigationRoot, ('Manager', ))
