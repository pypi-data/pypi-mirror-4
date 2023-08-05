""" Discover view controllers
"""
from zope.interface import implements
from zope.component import queryAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from eea.relations.interfaces import IAutoRelations
from AccessControl import Unauthorized
from eea.relations.discover.interfaces import IBrowserView

class View(BrowserView):
    """ Display auto discovered relations
    """
    implements(IBrowserView)

    def checkPermission(self, brains):
        """ Check document permission
        """
        mtool = getToolByName(self.context, 'portal_membership')
        for brain in brains:
            getObject = getattr(brain, 'getObject', None)
            if getObject:
                try:
                    brain = brain.getObject()
                except Unauthorized:
                    continue
            if mtool.checkPermission('View', brain):
                yield brain

    @property
    def tabs(self):
        """ Return brains
        """
        explorer = queryAdapter(self.context, IAutoRelations)
        if not explorer:
            return

        for tab, brains in explorer():
            brains = [b for b in self.checkPermission(brains)]
            if not len(brains):
                continue
            yield tab, brains
