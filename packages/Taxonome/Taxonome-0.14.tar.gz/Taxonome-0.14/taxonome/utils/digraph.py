from taxonome.external.graphs import MutableGraph, Directed, reversed
from collections import deque

class DiGraph(MutableGraph, Directed):
    """A very simple directional graph class. The implementation is a dict of
    sets, so arbitrary hashable objects can be used for the nodes."""
    class NodesView(MutableGraph.NodesView):
        def __contains__(self, node):
            return node in self.graph.data
            
        def __iter__(self):
            return iter(self.graph.data)
        
        def __len__(self):
            return len(self.graph.data)
        
        def discard(self, node):
            self.graph.data.pop(node, None)
            for _, successors in self.graph.data:
                successors.discard(node)
        
        def add(self, node):
            if node not in self.graph.data:
                self.graph.data[node] = set()
        
    class EdgesView(MutableGraph.EdgesView):
        def __contains__(self, edge):
            tail, head = edge
            return tail in self.graph.data and head in self.graph.data[tail]
            
        def __len__(self):
            return sum(len(links) for _, links in self.graph.data.items())
            
        def __iter__(self):
            for tail, links in self.graph.data.items():
                for head in links:
                    yield (tail, head)
                    
        def __getitem__(self, edge):
            if edge in self:
                return 1
            raise KeyError(edge)
        
        def __setitem__(self, edge, value):
            if value != 1:
                raise ValueError("Edge labels are not supported.")
            tail, head = edge
            self.graph.nodes.add(tail)
            self.graph.nodes.add(head)
            self.graph.data[tail].add(head)
            
        def __delitem__(self, edge):
            if edge not in self:
                raise KeyError(edge)
            tail, head = edge
            self.graph.data[tail].discard(head)
            
    def __init__(self):
        super(DiGraph, self).__init__()
        self.data = {}
    
    def __contains__(self, key):
        return key in self.data
        
    @classmethod
    def build(cls, edges, nodes=[]):
        g = cls()
        g.data = {n: set() for n in nodes}
        for t,h in edges:
            g.edges.add(t,h)
        return g
    
    def successors(self, node, depth_first=False):
        """Iterate over all successors of the given node.
        
        By default, it will look breadth first. If depth_first is True, it will
        look depth first.
        """
        stq = deque()
        push = stq.extend if depth_first else stq.extendleft
        push(self.data[node])
        already_done = set([node])
        while stq:
            node = stq.pop()
            if node not in already_done:
                yield node
                push(self.data[node])
                already_done.add(node)

    def is_successor(self, predecessor, subject, depth_first=False):
        """Return True if subject is a successor of predecessor.
        
        By default, it will search breadth first. This can be changed by setting
        depth_first to True."""
        if subject in self.data[predecessor]:
            return True
        
        stq = deque()
        push = stq.extend if depth_first else stq.extendleft
        push(self.data[predecessor])
        already_done = set([predecessor])
        while stq:
            predecessor = stq.pop()
            if predecessor not in already_done:
                links = self.data[predecessor]
                if subject in links:
                    return True
                push(links)
                already_done.add(predecessor)
        
        return False
    
    def immediate_predecessors(self, node):
        """Iterate over the immediate predecessors of a given node."""
        for x, xchildren in self.data.items():
            if node in xchildren:
                yield x
    
    def predecessors(self, node):
        """Iterate over all predecessors of a node. Note that this is slower
        than iterating over successors."""
        stq = deque(self.immediate_predecessors(node))
        already_done = set([node])
        while stq:
            nextnode = stq.pop()
            if nextnode not in already_done:
                yield nextnode
                stq.extend(self.immediate_predecessors(nextnode))
                already_done.add(nextnode)

# We need to alias these classes here for pickle to accept DiGraph instances.
NodesView = DiGraph.NodesView
EdgesView = DiGraph.EdgesView
