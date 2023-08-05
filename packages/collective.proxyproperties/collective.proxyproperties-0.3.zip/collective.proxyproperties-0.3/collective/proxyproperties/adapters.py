from persistent.dict import PersistentDict

from zope.annotation.interfaces import IAnnotations
from zope.app.component.interfaces import ISite
from zope.interface import implements
from zope.component import adapts

from collective.proxyproperties.interfaces import IProxyPropertyAble

PROXY_PROPERTIES = 'collective.proxyproperties.propertyoverrides'


class ProxyProperties(object):
    """This adapter allows us to set and retrieve properties from the
    proxy property annotation on the ISite object.
    """
    implements(IProxyPropertyAble)
    adapts(ISite)
    
    def __init__(self, context):
        self.context = context
        self.annos = IAnnotations(self.context)
        if PROXY_PROPERTIES not in self.annos:
            self.annos[PROXY_PROPERTIES] = PersistentDict()
    
    def getProperty(self, prop_sheet_id, prop_id, default=None):
        """Get a specific property from a property sheet, a default
        can be passed in.
        """
        prop_sheet = self.getPropertySheet(prop_sheet_id)
        if prop_id in prop_sheet:
            return prop_sheet[prop_id]
        return default
    
    def setPropertySheet(self, prop_sheet_id):
        """Create a new PersistentDict if the property sheet does
        not yet exist
        """
        if not prop_sheet_id in self.annos[PROXY_PROPERTIES]:
            self.annos[PROXY_PROPERTIES][prop_sheet_id] = PersistentDict()
        
    def getPropertySheet(self, prop_sheet_id):
        """Get a property sheet by it's ID
        """
        self.setPropertySheet(prop_sheet_id)
        return self.annos[PROXY_PROPERTIES][prop_sheet_id]
    
    def setProperty(self, prop_sheet_id, prop_id, value):
        """Set a property on a given property sheet
        """
        self.setPropertySheet(prop_sheet_id)
        self.annos[PROXY_PROPERTIES][prop_sheet_id][prop_id] = value
    
    def clearProperty(self, prop_sheet_id, prop_id):
        """Remove a property from the property sheet
        """
        prop_sheet = self.getPropertySheet(prop_sheet_id)
        if prop_id in prop_sheet:
            del prop_sheet[prop_id]

