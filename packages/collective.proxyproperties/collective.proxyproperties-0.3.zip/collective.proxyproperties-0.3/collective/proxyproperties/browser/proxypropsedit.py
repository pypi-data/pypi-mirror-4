from zope.component import getMultiAdapter
from zope.interface import implements
from zope.interface import Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from collective.proxyproperties.interfaces import IProxyPropertyAble

# XXX this doesn't cover all prop types
PROP_FIELD_TYPES_MAPPING = {
    'boolean': 'checkbox',
    'lines': 'textarea',
    'text': 'textarea',
    'string': 'text',
    'int': 'text'
}

def asbool(s):
    s = str(s).strip()
    return s.lower() in ('t', 'true', 'y', 'yes', 'on', '1')


class IProxyPropertiesEdit(Interface):
    """
    ProxyPropertiesEdit view interface
    """

    def getPropertySheetIds():
        """Get a list of available property sheet IDs
        """

    def getPropsForSheet(prop_sheet_id):
        """Return the props and type for the given sheet
        """

    def decipherPropFieldType(prop_type):
        """Figure out what kind of field a property type maps to
        """

    def getDefaultValue(prop_sheet_id, prop_id):
        """get the current value of the property
        """


class ProxyPropertiesEdit(BrowserView):
    """
    ProxyPropertiesEdit browser view
    """
    implements(IProxyPropertiesEdit)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        portal_state = getMultiAdapter((self.context, self.request),
                                         name=u"plone_portal_state")
        self.portal = portal_state.portal()
        # directly access the properties tool
        # XXX recursively go up the tree to get this instead
        self.portal_props = self.portal.portal_properties
        self.local_props = getToolByName(self.context, 'portal_properties')
        # only take care of the form if it was actually submitted
        if self.request.get('form.submitted', False) == 'True':
            self.processForm()

    def processForm(self):
        proxy_props = IProxyPropertyAble(self.context)
        # figure out which 'form' was saved
        for prop_sheet_id in self.getPropertySheetIds():
            if self.request.get("form.%s.save" % prop_sheet_id, False):
                break
        prop_map = self._getPropMap(prop_sheet_id)
        form_values = self.request.form

        for prop_id in prop_map:
            prop_type = prop_map[prop_id]
            form_prop_id = 'form.%s.%s' % (prop_sheet_id, prop_id)
            prop_value = form_values.get(form_prop_id, '')
            # convert values to the appropriate type
            if prop_type == 'lines':
                if prop_value:
                    # split on new lines for lines field
                    prop_value = tuple(prop_value.split('\r\n'))
                else:
                    prop_value = tuple()
            elif prop_type == 'boolean':
                prop_value = asbool(prop_value)
            elif prop_type == 'int':
                # XXX this will error out if not set correctly
                prop_value = int(prop_value)

            original_value = self._getOriginalValue(prop_sheet_id, prop_id)
            # check to see if the property has been changed
            # TODO this doesn't work completely...
            if prop_value != original_value:
                proxy_props.setProperty(prop_sheet_id, prop_id, prop_value)
            else:
                proxy_props.clearProperty(prop_sheet_id, prop_id)

        # clear properties that have the reset flag set in the form
        map(lambda x: proxy_props.clearProperty(*x.split('.')),
            form_values.get('form.reset_defaults', []))

        # set the status message and redirect
        message = "Properties for %s saved" % prop_sheet_id
        IStatusMessage(self.request).addStatusMessage(message, 'info')
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def getPropertySheetIds(self):
        return self.portal_props.objectIds()

    def getPropsForSheet(self, prop_sheet_id):
        prop_sheet = self.portal_props[prop_sheet_id]
        return prop_sheet.propertyMap()

    def decipherPropFieldType(self, prop_type):
        if prop_type in PROP_FIELD_TYPES_MAPPING:
            return PROP_FIELD_TYPES_MAPPING[prop_type]
        return None

    def _getPropMap(self, prop_sheet_id):
        """get a mapping of property IDs and property types

        XXX should probably get rid of this and use propertyMap as is
            since it includes the 'mode'
        """
        prop_map = [
            (i['id'], i['type'])
            for i in self.getPropsForSheet(prop_sheet_id)
            ]
        return dict(prop_map)

    def getDefaultValue(self, prop_sheet_id, prop_id):
        prop_map = self._getPropMap(prop_sheet_id)
        prop_sheet = getattr(self.local_props, prop_sheet_id)
        prop = prop_sheet.getProperty(prop_id, '')
        if prop_map[prop_id] == 'lines':
            return '\n'.join(prop)
        if prop_map[prop_id] == 'boolean':
            if prop:
                return 'checked'
            else:
                return ''
        return prop

    def _getOriginalValue(self, prop_sheet_id, prop_id):
        """Get the original value set in portal_properties
        """
        prop_sheet = getattr(self.portal_props, prop_sheet_id)
        return prop_sheet.getProperty(prop_id, None)

