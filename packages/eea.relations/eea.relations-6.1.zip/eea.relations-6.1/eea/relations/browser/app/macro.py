""" View macro utils
"""
from Products.Five.browser import BrowserView
from eea.relations.component import getForwardRelationWith
from eea.relations.component import getBackwardRelationWith
from Products.CMFCore.utils import getToolByName


class Macro(BrowserView):
    """ Categorize relations
    """

    def __init__(self, context, request):
        super(Macro, self).__init__(context, request)
        self._portal_membership = None

    @property
    def portal_membership(self):
        """ cached portal_membership as a property of Macro
        """
        if not self._portal_membership:
            self._portal_membership = getToolByName(self.context,
                                                          'portal_membership')
        return self._portal_membership

    def checkPermission(self, doc):
        """ Check document permission
        """
        mtool = self.portal_membership
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

        contentTypes = {}
        nonForwardRelations = set()
        relations = accessor()
        for relation in relations:
            if not self.checkPermission(relation) or relation.portal_type in \
                    nonForwardRelations:
                continue
            portalType = relation.portal_type

            if portalType not in contentTypes:
                forward = getForwardRelationWith(self.context, relation)
                if not forward:
                    nonForwardRelations.add(portalType)
                    continue
                name = forward.getField('forward_label').getAccessor(forward)()
                contentTypes[portalType] = name

            name = contentTypes[portalType]
            if name not in tabs:
                tabs[name] = []
            tabs[name].append(relation)
        tabs = tabs.items()
        tabs.sort()
        # sort by effective date reversed by default
        for _label, relations in tabs:
            relations.sort(cmp=lambda x, y:cmp(x.effective(),
                                               y.effective()),
                           reverse=True)
        return tabs

    def backward(self, **kwargs):
        """ Return backward relations by category
        """
        tabs = {}
        getBRefs = getattr(self.context, 'getBRefs', None)
        if not getBRefs:
            return tabs

        relation = kwargs.get('relation', 'relatesTo')

        relations = getBRefs(relation) or []
        contentTypes = {}
        nonBackwardRelations = set()
        for relation in relations:
            # save the name and the portal type of the first relation that we
            # have permission to use.
            # this way we can check if other relations are of same portal_type
            # if they are then we don't need to check if it's a backward
            # relation and what is it's name, we can just add it to the tabs
            # for that relation name the relation item
            if not self.checkPermission(relation) or relation.portal_type in \
                    nonBackwardRelations:
                continue
            portalType = relation.portal_type
            # if the portal_type of the relation is not already in
            # contentTypes than we are dealing with a backward relation that
            # is different from the ones we had before therefore we need
            if portalType not in contentTypes:
                backward = getBackwardRelationWith(self.context, relation)
                if not backward:
                    nonBackwardRelations.add(portalType)
                    continue
                name = backward.getField('backward_label').getAccessor(
                                                                   backward)()
                contentTypes[portalType] = name

            name = contentTypes[portalType]
            if name not in tabs:
                tabs[name] = []
            tabs[name].append(relation)
        tabs = tabs.items()
        tabs.sort() #this sorts based on relation label

        # sort by effective date reversed by default
        for _label, relations in tabs:
            relations.sort(cmp=lambda x, y:cmp(x.effective(),
                                               y.effective()),
                           reverse=True)
        return tabs
