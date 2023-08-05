# See also permissions.zcml, but we define them here in python too so
# they can be imported.
from Products.CMFCore import permissions as CMFCorePermissions
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('collective.proxyproperties')
security.declarePublic('ManageProperties')
ManageProperties = "collective.proxyproperties: ManageProperties"
setDefaultRoles(ManageProperties, ( 'Manager',) )
