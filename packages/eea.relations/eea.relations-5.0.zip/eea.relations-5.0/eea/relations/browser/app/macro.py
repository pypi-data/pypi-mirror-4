""" View macro utils
"""
from Products.Five.browser import BrowserView
from eea.relations.component import getForwardRelationWith
from eea.relations.component import getBackwardRelationWith
from Products.CMFCore.utils import getToolByName

class Macro(BrowserView):
    """ Categorize relations
    """
    def checkPermission(self, doc):
        """ Check document permission
        """
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission('View', doc):
            return doc
        return None

    def forward(self, **kwargs):
        """ Return forward relations by category
        """
        tabs = {}
         
        fieldname = kwargs.get('fieldname', 'relatedItems')
        field = self.context.getField(fieldname)
        if not field:
            return tabs

        accessor = field.getAccessor(self.context)
        #getRelatedItems = getattr(self.context, 'getRelatedItems', None)

        relations = accessor()
        for relation in relations:
            if not self.checkPermission(relation):
                continue

            forward = getForwardRelationWith(self.context, relation)
            if not forward:
                continue

            name = forward.getField('forward_label').getAccessor(forward)()
            if name not in tabs:
                tabs[name] = []
            tabs[name].append(relation)
        tabs = tabs.items()
        tabs.sort()
        return tabs

    def backward(self, **kwargs):
        """ Return backward relations by category
        """
        tabs = {}
        getBRefs = getattr(self.context, 'getBRefs', None)
        if not getBRefs:
            return tabs

        relation = kwargs.get('relation', 'relatesTo')

        relations = getBRefs(relation)
        for relation in relations:
            if not self.checkPermission(relation):
                continue

            backward = getBackwardRelationWith(self.context, relation)
            if not backward:
                continue

            name = backward.getField('backward_label').getAccessor(backward)()
            if name not in tabs:
                tabs[name] = []
            tabs[name].append(relation)
        tabs = tabs.items()
        tabs.sort()
        return tabs
