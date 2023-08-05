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
    def __init__(self, context, request):
        """ BaseGraph Init
        """
        super(BaseGraph, self).__init__(context, request)
        self.pt_relations = getToolByName(self.context, 'portal_relations')
        self.graph_res = PyGraph()

    @property
    def graph(self):
        """ Generate pydot.Graph
        """
        graph_res = self.graph_res
        graph_string = graph_res.to_string()
        if graph_string == "digraph G {\n}\n":
            self.markBrokenRelations()
            graph_res = self.graph_res
        # we need to have an empty PyGraph object on graph_res otherwise when 
        # ran on the same object it misses results when new restrictions are 
        # added to relations tool
        self.graph_res = PyGraph()
        return graph_res

    def image(self):
        """ Returns a PNG image
        """
        image = queryUtility(IGraph, name=u'png')
        raw = image(self.graph)

        self.request.response.setHeader('Content-Type', 'image/png')
        return raw

    def brokenRelationMessage(self, bad_content, bad_relations):
        """ Broken relation portal status message
        """
        return {u'relations': bad_relations, u'content': bad_content}

    def markBrokenRelations(self):
        """ Base method which assignes a pydot.Graph for the graph method
        """
        self.graph_res = PyGraph()

class RelationGraph(BaseGraph):
    """ Draw a graph for Relation
    """

    def markBrokenRelations(self):
        """ Construct graph and return message with info about broken 
        relations for RelationGraph if any errors are found
        """ 
        bad_relations = []
        bad_content = []
        bad_rel = ""

        graph = PyGraph()
        value_from = self.context.getField('from').getAccessor(self.context)()
        nfrom = self.pt_relations.get(value_from)
        if nfrom:
            node = queryAdapter(nfrom, INode)
            graph.add_node(node())

        value_to = self.context.getField('to').getAccessor(self.context)()
        nto = self.pt_relations.get(value_to)
        if not (value_from == value_to) and nto:
            node = queryAdapter(nto, INode)
            graph.add_node(node())

        edge = queryAdapter(self.context, IEdge)
        res = edge()
        if res:
            graph.add_edge(res)
            self.graph_res = graph
            return ""

        if not nfrom:
            bad_rel = value_from
        if not nto:
            bad_rel = value_to
        relation = self.pt_relations[self.context.getId()]
        if bad_rel and bad_rel not in bad_content:
            bad_content.append(bad_rel)
            bad_relations.append(relation.Title())
            self.graph_res = graph
            return self.brokenRelationMessage(bad_content, bad_relations)


class ContentTypeGraph(BaseGraph):
    """ Draw a graph for ContentType
    """

    def markBrokenRelations(self):
        """ Construct graph and return message with info about broken 
        relations for ContentTypeGraph if any errors are found
        """
        bad_relations = []
        bad_content = [] 
        name = self.context.getId()
        node = queryAdapter(self.context, INode)
        graph = PyGraph()
        graph.add_node(node())
        tool = queryAdapter(self.context, IToolAccessor)
        relations = tool.relations(proxy=False)
        for relation in relations:
            field = relation.getField('to')
            value_from = field.getAccessor(relation)()
            field = relation.getField('from')
            value_to = field.getAccessor(relation)()
            if name == value_from:
                nto = self.pt_relations.get(value_to)
                if not (value_from == value_to
                    ) and nto:
                    node = queryAdapter(nto, INode)
                    graph.add_node(node())
                edge = queryAdapter(relation, IEdge)
                res = edge()
                if res:
                    graph.add_edge(res)
                else:
                    if value_to not in bad_content:
                        bad_content.append(value_to)
                    bad_relations.append(relation.Title())
                # if we don't continue when value_from == name
                # then we will get a double "node-myX" -> "node-myX"
                # graph entry when value_to is also equal to name
                continue

            if name == value_to:
                nfrom = self.pt_relations.get(value_from)
                if not (value_from == value_to
                    ) and nfrom:
                    node = queryAdapter(nfrom, INode)
                    graph.add_node(node())
                edge = queryAdapter(relation, IEdge)
                res = edge()
                if res:
                    graph.add_edge(res)
                else:
                    if value_from not in bad_content:
                        bad_content.append(value_from)
                    bad_relations.append(relation.Title())

        self.graph_res = graph
        if bad_relations:
            return self.brokenRelationMessage(bad_content, bad_relations)
        return ""

class ToolGraph(BaseGraph):
    """ Draw a graph for portal_relations
    """

    def markBrokenRelations(self):
        """ Construct graph and return message with info about broken 
        relations for ToolGraph if any errors are found
        """
        bad_relations = []
        bad_content = [] 
        bad_rel = ""

        graph = PyGraph()
        tool = queryAdapter(self.context, IToolAccessor)
        types = tool.types(proxy=False)
        for ctype in types:
            node = queryAdapter(ctype, INode)
            graph.add_node(node())

        relations = tool.relations(proxy=False)
        for relation in relations:
            edge = queryAdapter(relation, IEdge)
            res = edge()
            if res:
                graph.add_edge(res)
                continue
            else:
                # if no result then check which relation id is missing
                from_rel = relation['from']
                to_rel = relation['to']
                pr_from = self.pt_relations.get(from_rel)
                pr_to = self.pt_relations.get(to_rel)
                if not pr_from:
                    bad_rel = from_rel
                if not pr_to:
                    bad_rel = to_rel
                if bad_rel and bad_rel not in bad_content:
                    bad_content.append(bad_rel)
                bad_relations.append(relation.Title())

        self.graph_res = graph
        if bad_relations:
            return self.brokenRelationMessage(bad_content, bad_relations)
        return ""

    def dot(self):
        """ Return dotted graph 
        """
        return self.graph.to_string()
