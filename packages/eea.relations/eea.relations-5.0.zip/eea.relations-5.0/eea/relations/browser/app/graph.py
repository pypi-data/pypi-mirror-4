""" Graph drawers
"""
from pydot import Dot as PyGraph
from zope.component import queryAdapter, queryUtility
from Products.Five.browser import BrowserView

from eea.relations.interfaces import INode
from eea.relations.interfaces import IEdge
from eea.relations.interfaces import IGraph
from eea.relations.interfaces import IToolAccessor
from Products.CMFCore.utils import getToolByName

class BaseGraph(BrowserView):
    """ Abstract layer
    """
    @property
    def graph(self):
        """ Returns a pydot.Graph instance
        """
        return PyGraph()

    def image(self):
        """ Returns a PNG image
        """
        image = queryUtility(IGraph, name=u'png')
        raw = image(self.graph)

        self.request.response.setHeader('Content-Type', 'image/png')
        return raw

class RelationGraph(BaseGraph):
    """ Draw a graph for Relation
    """
    @property
    def graph(self):
        """ Generate pydot.Graph
        """
        rtool = getToolByName(self.context, 'portal_relations')
        graph = PyGraph()

        nfrom = self.context.getField('from')
        value_from = nfrom.getAccessor(self.context)()
        if value_from in rtool.objectIds():
            nfrom = rtool[value_from]
            node = queryAdapter(nfrom, INode)
            graph.add_node(node())

        nto = self.context.getField('to')
        value_to = nto.getAccessor(self.context)()
        if not (value_from == value_to) and (value_to in rtool.objectIds()):
            nto = rtool[value_to]
            node = queryAdapter(nto, INode)
            graph.add_node(node())

        edge = queryAdapter(self.context, IEdge)
        graph.add_edge(edge())
        return graph

class ContentTypeGraph(BaseGraph):
    """ Draw a graph for ContentType
    """
    @property
    def graph(self):
        """ Generate pydot.Graph
        """
        rtool = getToolByName(self.context, 'portal_relations')
        name = self.context.getId()
        node = queryAdapter(self.context, INode)

        tool = queryAdapter(self.context, IToolAccessor)
        docs = tool.relations(proxy=False)

        graph = PyGraph()
        graph.add_node(node())

        for doc in docs:
            field = doc.getField('to')
            value_from = field.getAccessor(doc)()
            field = doc.getField('from')
            value_to = field.getAccessor(doc)()
            if name == value_from:
                if not (value_from == value_to
                    ) and value_to in rtool.objectIds():
                    nto = rtool[value_to]
                    node = queryAdapter(nto, INode)
                    graph.add_node(node())

                edge = queryAdapter(doc, IEdge)
                graph.add_edge(edge())
                continue

            if name == value_to:
                if not (value_from == value_to
                    ) and value_from in rtool.objectIds():
                    nfrom = rtool[value_from]
                    node = queryAdapter(nfrom, INode)
                    graph.add_node(node())

                edge = queryAdapter(doc, IEdge)
                graph.add_edge(edge())
                continue

        return graph

class ToolGraph(BaseGraph):
    """ Draw a graph for portal_relations
    """
    @property
    def graph(self):
        """ Generate pydot.Graph
        """
        graph = PyGraph()
        tool = queryAdapter(self.context, IToolAccessor)
        docs = tool.types(proxy=False)
        for doc in docs:
            node = queryAdapter(doc, INode)
            graph.add_node(node())

        docs = tool.relations(proxy=False)
        for doc in docs:
            edge = queryAdapter(doc, IEdge)
            graph.add_edge(edge())

        return graph

    def dot(self):
        """ Return dotted graph """
        return self.graph.to_string()
