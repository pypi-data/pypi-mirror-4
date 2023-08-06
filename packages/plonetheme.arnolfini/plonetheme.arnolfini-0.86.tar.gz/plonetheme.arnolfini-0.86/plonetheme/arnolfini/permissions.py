from Products.CMFCore import permissions as CMFCorePermissions
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('plonetheme.arnolfini')

security.declarePublic('MakeBuyable')
MakeBuyable = 'Arnolfini: MakeBuyable'
setDefaultRoles(MakeBuyable, ())