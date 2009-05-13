from persistent import Persistent
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from zope.app.component.hooks import getSite
from Products.CMFCore.interfaces import IPropertiesTool
#from five.localsitemanager import find_next_sitemanager

import logging
logger = logging.getLogger(__name__)

_marker = object()
PROXY_PROPERTIES = 'collective.proxyproperties.propertyoverrides'

class ProxyProperties(Persistent):
    """A proxy object to gather properties
    """
    implements(IPropertiesTool)
    
    def __getattribute__(self, name):
        # XXX we only replicate property sheets set in
        #     the portal_properties tool.  I would like to
        #     be able to recurse up to get to the real prop
        #     sheet eventually.
        portal = getSite()
        prop_sheets = portal.portal_properties.objectIds()
        if name in prop_sheets:
            #parent_sm = find_next_sitemanager(self)
            parent_props = portal.portal_properties
            return FakePropertySheet(parent_props[name])
        return super(ProxyProperties, self).__getattribute__(name)


class FakePropertySheet(object):
    """Pretend like we are a property sheet.  Defer to the original
    if we haven't overridden the property that is requested.
    
    XXX: need to take care of all the prop sheet methods...
    """
    
    def _getProxyProperty(self, prop, default=None):
        """
        """
        portal = getSite()
        annos = IAnnotations(portal)
        ps_id = self.prop_sheet.id
        overrides = annos.get(PROXY_PROPERTIES, {}).get(ps_id, {})
        custom_prop = overrides.get(prop, _marker)
        if custom_prop is not _marker:
            return custom_prop
        # default back to the original
        return self.prop_sheet.getProperty(prop, default)
    
    def getProperty(self, prop, default=None):
        """
        """
        return self._getProxyProperty(prop, default)
    
    def __getattribute__(self, name):
        if name != "attrs_to_ignore" and name not in self.attrs_to_ignore:
            return self._getProxyProperty(name)
        return super(FakePropertySheet, self).__getattribute__(name)
    
    def __init__(self, prop_sheet):
        """
        """
        # attrs that we need to get from self
        self.attrs_to_ignore = [
            'prop_sheet',
            '_getProxyProperty',
            'getProperty'
            ]
        # a copy of the original property sheet
        self.prop_sheet = prop_sheet

