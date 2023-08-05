""" Events
"""
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides, noLongerProvides
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.context import SnapshotImportContext

from eea.relations.subtypes.interfaces import (
    IOriginalFacetedNavigable,
    IFacetedNavigable,
)

def subtype(obj, evt):
    """ Subtype as faceted navigable
    """
    context = obj
    portal_type = getattr(context, 'portal_type', None)
    if portal_type != 'EEARelationsContentType':
        return

    # Subtype as faceted navigable
    subtyper = queryMultiAdapter((context, context.REQUEST),
        name=u'faceted_search_subtyper', default=queryMultiAdapter(
            (context, context.REQUEST), name=u'faceted_subtyper'))

    if subtyper:
        subtyper.enable()

    # Add default widgets
    widgets = queryMultiAdapter((context, context.REQUEST),
                                name=u'default_widgets.xml')
    if not widgets:
        return

    xml = widgets()
    environ = SnapshotImportContext(context, 'utf-8')
    importer = queryMultiAdapter((context, environ), IBody)
    if not importer:
        return
    importer.body = xml

def faceted_enabled(doc, evt):
    """ EVENT: faceted navigation enabled
    """
    portal_type = getattr(doc, 'portal_type', None)
    if portal_type != 'EEARelationsContentType':
        return

    noLongerProvides(doc, IOriginalFacetedNavigable)
    alsoProvides(doc, IFacetedNavigable)
