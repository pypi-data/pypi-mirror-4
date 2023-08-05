""" Relations content-type components
"""
from zope.component import queryAdapter
from zope.interface import implements
from Products.Five.utilities.interfaces import IMarkerInterfaces
from eea.relations.interfaces import IToolAccessor
from eea.relations.component.interfaces import IContentTypeLookUp

class ContentTypeLookUp(object):
    """ Lookup for context in portal_relations content-types """

    implements(IContentTypeLookUp)

    def __init__(self, context):
        self.context = context
        self.adapted = None
        self._ctypes = None

    @property
    def ctypes(self):
        """ Types
        """
        if self._ctypes:
            return self._ctypes

        tool = queryAdapter(self.context, IToolAccessor)
        if not tool:
            return []
        self._ctypes = [doc for doc in tool.types(proxy=False)]
        return self._ctypes

    @property
    def portal_type(self):
        """ Context portal_type
        """
        return getattr(self.context, 'portal_type', '')

    @property
    def object_provides(self):
        """ Context object_provides
        """
        if not self.adapted:
            self.adapted = IMarkerInterfaces(self.context)

        ifaces = self.adapted.getDirectlyProvidedNames()
        ifaces.extend(self.adapted.getInterfaceNames())
        return ifaces

    @property
    def tuple_types(self):
        """ Types
        """
        res = {}
        for doc in self.ctypes:
            ct_type = doc.getField('ct_type').getAccessor(doc)()
            if not ct_type:
                continue
            ct_interface = doc.getField('ct_interface').getAccessor(doc)()
            if not ct_interface:
                continue
            res[(ct_interface, ct_type)] = doc
        return res

    @property
    def portal_types_only(self):
        """ Only portal_types
        """
        res = {}
        for doc in self.ctypes:
            ct_interface = doc.getField('ct_interface').getAccessor(doc)()
            if ct_interface:
                continue
            ct_type = doc.getField('ct_type').getAccessor(doc)()
            if not ct_type:
                continue
            res[ct_type] = doc
        return res

    @property
    def interfaces_only(self):
        """ Only interfaces
        """
        res = {}
        for doc in self.ctypes:
            ct_type = doc.getField('ct_type').getAccessor(doc)()
            if ct_type:
                continue
            ct_interface = doc.getField('ct_interface').getAccessor(doc)()
            if not ct_interface:
                continue
            res[ct_interface] = doc
        return res

    def __call__(self, **kwargs):
        """ Return ContentType object from portal_relation or None
        """
        # Search for full mapping
        tuple_types = self.tuple_types
        ptype = self.portal_type
        for iface in self.object_provides:
            if (iface, ptype) in tuple_types:
                return tuple_types[(iface, ptype)]

        # Fallback to portal_type only
        portal_types = self.portal_types_only
        if ptype in self.portal_types_only:
            return portal_types[ptype]

        # Fallback to interfaces only
        interfaces = self.interfaces_only
        for iface in self.object_provides:
            if iface in interfaces:
                return interfaces[iface]

        return None
