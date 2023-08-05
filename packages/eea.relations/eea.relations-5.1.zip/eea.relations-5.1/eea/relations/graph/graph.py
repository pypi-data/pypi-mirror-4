""" Graph utilities
"""
import os
from tempfile import mktemp
from zope.interface import implements
from eea.relations.graph.interfaces import IGraph
from eea.relations.config import GRAPHVIZ_PATHS

class Graph(object):
    """ Generates a PNG graph
    """
    implements(IGraph)

    def __init__(self, fmt):
        self.fmt = fmt

    def __call__(self, graph):
        """ Draw pydot.Graph
        """
        if GRAPHVIZ_PATHS:
            graph.progs = GRAPHVIZ_PATHS

        writter = getattr(graph, 'write_' + self.fmt, None)
        if not writter:
            return None

        path = mktemp('.%s'  % self.fmt)
        img = writter(path=path)

        img = open(path, 'rb')
        raw = img.read()

        img.close()
        os.remove(path)

        return raw

PNG = Graph('png')
