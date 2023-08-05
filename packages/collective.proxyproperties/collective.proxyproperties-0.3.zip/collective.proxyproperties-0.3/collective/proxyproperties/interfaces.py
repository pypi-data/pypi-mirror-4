from zope.interface import Interface

class IProxyPropertyAble(Interface):
    """Interface used to adapt a site root and add proxy
    properties
    """
    
    def getProperty(prop_sheet_id, prop_id, default=None):
        """Get a specific property from a property sheet, a default
        can be passed in.
        """
    
    def setPropertySheet(prop_sheet_id):
        """Create a new PersistentDict if the property sheet does
        not yet exist
        """
        
    def getPropertySheet(prop_sheet_id):
        """Get a property sheet by it's ID
        """
    
    def setProperty(prop_sheet_id, prop_id, value):
        """Set a property on a given property sheet
        """
    
    def clearProperty(prop_sheet_id, prop_id):
        """Remove a property from the property sheet
        """

