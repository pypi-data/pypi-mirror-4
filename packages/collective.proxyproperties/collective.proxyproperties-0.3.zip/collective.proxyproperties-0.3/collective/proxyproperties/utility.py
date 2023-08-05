import re

from OFS.interfaces import ITraversable
from persistent import Persistent

from zope.interface import implements
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter

from Products.CMFCore.interfaces import IPropertiesTool

# KSS
try:
    from kss.core.interfaces import IKSSView
    HAS_KSS = True
except ImportError:
    HAS_KSS = False

from collective.proxyproperties.interfaces import IProxyPropertyAble

import zope.i18nmessageid
proxypropertiesMessageFactory = zope.i18nmessageid.MessageFactory("collective.proxyproperties")

_marker = object()

unproxied_attrs_pattern = re.compile(r'^(_p_.*|__.*__)$')


def findSiteRoot():
    """Method to get the site root from the KSS
    site root.  MADNESS.
    """
    site_root = getSite()
    # If the KSS is in use, it has its own site root :(
    if HAS_KSS and IKSSView.providedBy(site_root):
        context = site_root.context
        request = site_root.request
        # get the portal via the plone util view
        portal_state = getMultiAdapter((context, request),
                                       name=u"plone_portal_state")
        site_root = portal_state.portal()
    return site_root


class ProxyProperties(Persistent):
    """A proxy object to gather properties
    """
    implements(IPropertiesTool)

    # XXX is this evil needed?  set security properly...
    __allow_access_to_unprotected_subobjects__ = True

    def __getattribute__(self, name):
        # For special attributes and persistence, we act like
        # ourselves
        if unproxied_attrs_pattern.match(name) is not None:
            return super(ProxyProperties, self).__getattribute__(name)

        portal_properties = findSiteRoot().portal_properties
        if name == 'objectIds':
            return getattr(portal_properties, name)

        # XXX we only replicate property sheets set in
        #     the portal_properties tool.  I would like to
        #     be able to recurse up to get to the real prop
        #     sheet eventually.
        prop_sheets = portal_properties.objectIds()
        if name in prop_sheets:
            parent_props = portal_properties
            return FakePropertySheet(parent_props[name])
        return super(ProxyProperties, self).__getattribute__(name)

    def getProperty(self, name, default=None):
        portal = findSiteRoot()
        prop_sheet = portal.portal_properties
        return prop_sheet.getProperty(name, default)

    def hasProperty(self, name):
        portal = findSiteRoot()
        prop_sheet = portal.portal_properties
        return prop_sheet.hasProperty(name)

    def __contains__(self, name):
        return name in self.objectIds()


class FakePropertySheet(Persistent):
    """Pretend like we are a property sheet.  Defer to the original
    if we haven't overridden the property that is requested.

    XXX: need to take care of all the prop sheet methods...
    XXX: not completely implementing ITraversable yet...
    """
    implements(ITraversable)

    # XXX is this evil needed?  set security properly...
    __allow_access_to_unprotected_subobjects__ = True

    def __init__(self, prop_sheet):
        # a copy of the original property sheet
        self.prop_sheet = prop_sheet
        self.prop_sheet_ids = prop_sheet.propertyIds()

    def __getattribute__(self, name):
        # we only want to short circuit for properties
        if name != "prop_sheet_ids" and name in self.prop_sheet_ids:
            return self._getProxyProperty(name)
        return super(FakePropertySheet, self).__getattribute__(name)

    def unrestrictedTraverse(self, path, default=None, restricted=0):
        return getattr(self, path)

    def restrictedTraverse(self, path, default=None):
        return self.unrestrictedTraverse(path, default)

    def _getProxyProperty(self, prop, default=None):
        portal = findSiteRoot()
        # if for some reason we can't adapt, pass off to the
        # default property sheet
        try:
            proxy_props = IProxyPropertyAble(portal)
            custom_prop = proxy_props.getProperty(
                self.prop_sheet.id,
                prop,
                _marker
                )
            if custom_prop is not _marker:
                return custom_prop
        except TypeError:
            pass
        # default back to the original
        return self.prop_sheet.getProperty(prop, default)

    def getProperty(self, prop, default=None):
        return self._getProxyProperty(prop, default)

    def hasProperty(self, prop):
        return self.prop_sheet.hasProperty(prop)

