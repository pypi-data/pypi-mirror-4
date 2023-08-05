""" Browser view for bad relations listing
"""
from zope.component import queryAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from eea.relations.interfaces import IToolAccessor
from eea.relations.component import getForwardRelationWith
from Products.statusmessages.interfaces import IStatusMessage
import logging

logger = logging.getLogger('eea.relations.browser.badrelations')

class View(BrowserView):
    """ Views
    """
    def __call__(self):
        """ View
        """
        status = queryAdapter(self.request, IStatusMessage)
        if status:
            status.addStatusMessage('Be aware that this operation can \
                take a long time to perform if a lot of objects are \
                involved.', type='info')

        return self.index()

    @property
    def content_types(self):
        """ Content types
        """
        tool = queryAdapter(self.context, IToolAccessor)
        if not tool:
            return

        for brain in tool.types():
            yield brain

    @property
    def get_objects(self):
        """ Get objects
        """
        query = {}
        res = []

        catalog = getToolByName(self.context, 'portal_catalog')
        pr_tool = getToolByName(self.context, 'portal_relations')

        ct_type = self.request.get('ct_type', '')

        if ct_type:
            pr_ct_type = pr_tool[ct_type]

            query['sort_on'] = 'sortable_title'
            if pr_ct_type.getCt_type():
                query['portal_type'] = pr_ct_type.getCt_type()
            if pr_ct_type.getCt_interface():
                query['object_provides'] = pr_ct_type.getCt_interface()
            res = catalog(**query)

        return res

    @property
    def bad_relations_report(self):
        """ Get bad relations
        """
        logger.info('Start generating bad relations report.')
        res = []
        report = []

        # Get portal relations content type
        res = self.get_objects

        # Get relations
        for brain in res:
            bad_relations = []
            obj = brain.getObject()

            try:
                fwd = obj.getRelatedItems()
                # Check for bad relations
                for rel in fwd:
                    if not getForwardRelationWith(obj, rel):
                        bad_relations.append(rel)
                report.append((obj.Title(), obj, bad_relations))
            except (TypeError, ValueError):
                # The catalog expects AttributeErrors when
                # a value can't be found
                raise AttributeError
            except:
                logger.info('ERROR getting relations for %s' % brain.getURL())

        report.sort()
        logger.info('Done generating bad relations report.')
        return report
