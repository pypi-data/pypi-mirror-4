"""
Graph ABC, written by Matteo Dell'Amico for Python 3.

http://www.linux.it/~della/GraphABC/

(MIT license obtained by e-mail)
"""
#Copyright (c) 2009 Matteo Dell'Amico

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from abc import ABCMeta, abstractmethod
from collections import Set, Mapping, MutableSet, MutableMapping

class Graph(metaclass=ABCMeta):
    """Graph abstract base class.

    Edges are always labeled, with a default label of 1.

    The following invariants always apply:
    (n1, n2) in g.edges implies {n1, n2} <= g.nodes
    n not in g.nodes implies all(n not in edge for edge in g.edges)
    """

    class NodesView(Set):
        """ABC for the nodes."""

        def __init__(self, g):
            self.graph = g

    class EdgesView(Mapping):
        """ABC for the edges."""

        def __init__(self, g):
            self.graph = g

    def __init__(self):
        self.nodes = self.NodesView(self)
        self.edges = self.EdgesView(self)

    @abstractmethod
    def neighbors(self, node) -> Mapping:
        """Mapping from neighbors to label of corresponding edges.

        Do not try to modify the mapping resulting from this function:
        it may result in inconsistent behaviour.
        """

    @classmethod
    @abstractmethod
    def build(cls, edges, nodes=[]):
        """Returns a new graph with nodes and edges specified.

        If a node is present in edges but not in nodes, it will be added
        to nodes anyway.
        """

    @classmethod
    def copy_from(cls, g):
        """Returns a new graph with the same nodes and edges.

        An error is returned if a directed instance is called from an
        undirected one.
        """

        return cls.build(g.edges, g.nodes)

    def __eq__(self, other):
        return self.nodes == other.nodes and self.edges == other.edges

    def __ne__(self, other):
        return not (self == other)
    
class MutableGraph(Graph):

    @classmethod
    def from_graph(cls, g):
        res = cls()
        res.nodes |= g.nodes
        res.edges.update(g.edges)

    @classmethod
    def from_edges(cls, edges, nodes=[]):
        res = cls()
        res.nodes |= nodes
        res.edges.update(edges)

    class NodesView(MutableSet, Graph.NodesView):
        
        @abstractmethod
        def discard(self, node):
            """All edges incident to node should be discarded as well."""
    
    class EdgesView(MutableMapping, Graph.EdgesView):
        
        @abstractmethod
        def __setitem__(self, nodes, edge):
            """Nodes of the edge should be added to the graph's nodes."""

        # Convenience methods that add (default edge label: 1) and
        # discard edges mimicking a Set-like two-argument interface.

        def add(self, n1, n2):
            self[n1, n2] = 1

        def discard(self, n1, n2):
            try:
                del self[n1, n2]
            except KeyError:
                pass


class Directed(Graph):
    
    def outgoing(self, node):
        return {n2: v for (n1, n2), v in self.edges.items() if n1 == node}

    def incoming(self, node):
        return {n1: v for (n1, n2), v in self.edges.items() if n2 == node}

    neighbors = outgoing
    
class Undirected(Graph):

    def neighbors(self, node):
        res = {}
        for (n1, n2), v in self.edges.iteritems():
            if n1 == node:
                res[n2] = v
            elif n2 == node:
                res[n1] = v
        return res

def reversed(g: Directed):
    """Returns a copy of the graph with edge direction reversed."""
    
    return type(g).build((((n2, n1), v) for (n1, n2), v in g.edges.items()),
                         g.nodes)
                             
